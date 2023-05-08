from flask import request, make_response, jsonify
import jwt
from project.utils.log import logger
from project.config import JWT_SECRET_KEY
def jwt_required(func):
    def wrapper(*args, **kwargs):
        # 获取Authorization头部信息中的JWT令牌
        token = request.headers.get('Authorization')
        if token:
            try:
                # 使用JWT密钥验证JWT令牌
                request.payload_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
                # # 在请求的上下文中保存JWT负载
                logger.debug('解析token成功')
                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return make_response(jsonify(code=401, message='登录信息过期'), 401)
            except jwt.InvalidTokenError:
                return make_response(jsonify(code=401, message='非法登录'), 401)
        else:
            return make_response(jsonify(code=401, message='找不到登录信息'), 401)

    return wrapper