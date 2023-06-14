import datetime

from flask import request, make_response, jsonify
import jwt
from werkzeug.security import check_password_hash

from project.models import User, db
from project.utils.aes import encrypt
from project.utils.log import logger

# 定义JWT密钥和过期时间
JWT_SECRET_KEY = 'mewstore'
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)


def jwt_required(func):  # 用于验证JWT令牌
    def wrapper(*args, **kwargs):
        # 获取Authorization头部信息中的JWT令牌
        token = request.headers.get('Authorization')
        if token:
            try:
                # 使用JWT密钥验证JWT令牌
                request.payload_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
                # # 在请求的上下文中保存JWT负载
                logger.debug(f'用户id:{request.payload_id}解析token成功')
                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return make_response(jsonify(code=401, message='登录信息过期'), 401)
            except jwt.InvalidTokenError:
                return make_response(jsonify(code=401, message='非法登录'), 401)
        else:
            return make_response(jsonify(code=401, message='找不到登录信息'), 401)

    return wrapper


def check_status(status):  # 用于验证用户权限
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 检查JWT负载中是否包含指定权限
            user = db.session.query(User).get(request.payload_id)
            if user and user.status in status:
                request.user = user
                logger.debug(f'用户{user.username}鉴权成功')
                return func(*args, **kwargs)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)

        return wrapper

    return decorator


def after_get_info(args, login_type=None):  # 用于登录,用户名或手机号校验成功后的进一步操作，返回token
    # 验证用户登录信息
    if login_type == 'username':
        is_user = db.session.query(User).filter_by(username=args['username']).first()
        if is_user and check_password_hash(is_user.password, args['password']):
            user = is_user
        else:
            return make_response(jsonify(code=401, message='用户名或密码错误'), 401)
    if login_type == 'phone':
        if is_user := db.session.query(User).filter_by(phone_number=encrypt(args['phone_number'])).first():
            user = is_user
        else:
            return make_response(jsonify(code=401, message='用户不存在'), 401)
    # 构建JWT负载
    payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
               'id': user.id, 'status': user.status}
    # 生成JWT令牌
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    logger.debug(f'用户{user.username}登录成功')
    return make_response(jsonify(code=200, message='登录成功', token=token, status=user.status), 200)
