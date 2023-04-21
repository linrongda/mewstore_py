from werkzeug.security import generate_password_hash, check_password_hash

import data
import datetime
import jwt
from flask import request, jsonify, Blueprint
from flask_restful import Api, Resource, reqparse

# 定义应用和API
user = Blueprint('user', __name__)
api = Api(user)

# 定义JWT密钥和过期时间
JWT_SECRET_KEY = 'mewstore'
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)


# 定义装饰器进行JWT认证和权限检查
def jwt_required(func):
    def wrapper(*args, **kwargs):
        # 获取Authorization头部信息中的JWT令牌
        token = request.headers.get('Authorization')
        if token:
            try:
                # 使用JWT密钥验证JWT令牌
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                # 在请求的上下文中保存JWT负载
                request.jwt_payload = payload
                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return {'message': 'Token has expired'}, 401
            except jwt.InvalidTokenError:
                return {'message': 'Invalid token'}, 401
        else:
            return {'message': 'Token is missing'}, 401

    return wrapper


def check_status(status):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 检查JWT负载中是否包含指定权限
            if 'status' in request.jwt_payload and status in request.jwt_payload['status']:
                return func(*args, **kwargs)
            else:
                return {'message': 'Insufficient permissions'}, 403

        return wrapper

    return decorator


# 密码加密
def password_encrypt(pwd):
    return generate_password_hash(pwd)


# 验证密码
def check_password(password_hash, ckpwd):
    return check_password_hash(password_hash, ckpwd)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('check_password', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('status', type=int, required=True)
        args = parser.parse_args()
        if args['password'] != args['check_password']:
            return {'message': 'password not equal'}, 400
        if data.session.query(data.User).filter_by(nickname=args['nickname']).first():
            return {'message': 'nickname already exists'}, 400
        else:
            # 手机号验证(待添加)
            #
            try:
                user = data.User(nickname=args['nickname'], password=password_encrypt(args['password']),
                                 phone_number=args['phone_number'],
                                 status=args['status'])
                data.session.add(user)
                data.session.commit()
                return {'message': 'success'}, 200
            except:
                return {'message': 'error'}, 400


def after_get_info(args, type=None):
    # 验证用户登录信息
    users = data.session.query(data.User).all()
    if type=='nickname':
        for user in users:
            if user.nickname == args['nickname'] and check_password(user.nickname, args['password']):
                # 构建JWT负载
                payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
                           'nickname': user.nickname, 'status': user.status}
                # 生成JWT令牌
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                return {'token': token.decode('utf-8')}
    if type=='phone':
        for user in users:
            if user.phone_number == args['phone_number']:
                # 构建JWT负载
                payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
                           'nickname': user.nickname, 'status': user.status}
                # 生成JWT令牌
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                return {'token': token.decode('utf-8')}
    return {'message': 'Invalid username or password'}, 401


# 定义用户登录接口
class Login_Nickname(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        return after_get_info(args, type='nickname')


class Login_Phone(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True)
        args = parser.parse_args()
        #手机号验证(待添加)
        return after_get_info(args, type='phone')


# 定义需要JWT认证的API接口
class Users(Resource):
    # 使用装饰器进行JWT认证和权限检查
    @jwt_required
    @check_status('read')
    def get(self):
        return {'users': users}


class User(Resource):
    # 使用装饰器进行JWT认证和权限检查
    @jwt_required
    @check_status('read')
    def get(self, user_id):
        for user in users:
            if user['id'] == user_id:
                return {'user': user}
        return {'message': 'User not found'}, 404


# 添加API接口路由
api.add_resource(Register, '/register')
api.add_resource(Login_Nickname, '/login_nickname')
api.add_resource(Login_Phone, '/login_phone')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/int:user_id')
