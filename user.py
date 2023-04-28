import datetime

import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from data import User, db, app
from snowflake import id_generate
import qiniu

# 定义应用和API
user = Blueprint('user', __name__)
api = Api(user)

# 定义JWT密钥和过期时间
JWT_SECRET_KEY = 'mewstore'
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)


# 定义装饰器进行JWT认证和权限检查
def jwt_required(func):
    def wrapper(*args, **kwargs):
        # 获取Authorization头部信息中的JWT令牌
        token = request.headers.get('Authorization')
        if token:
            try:
                # 使用JWT密钥验证JWT令牌
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
                # # 在请求的上下文中保存JWT负载
                request.jwt_payload = payload
                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return make_response(jsonify(code=401, message='Token has expired'), 401)
            except jwt.InvalidTokenError:
                return make_response(jsonify(code=401, message='Invalid token'), 401)
        else:
            return make_response(jsonify(code=401, message='Token is missing'), 401)

    return wrapper


# def check_status(status):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             # 检查JWT负载中是否包含指定权限
#             if 'status' in request.jwt_payload and status in request.jwt_payload['status']:
#                 return func(*args, **kwargs)
#             else:
#                 return jsonify(code=403, message='Insufficient permissions'), 403
#
#         return wrapper
#
#     return decorator
class Sms(Resource):
    def get(self, phone_number):
        with app.app_context():
            if db.session.query(User).filter_by(phone_number=phone_number).first():
                return make_response(jsonify(code=400, message='phone_number already exists'), 400)
            else:
                # 手机号验证(待添加)

                return make_response(jsonify(code=200, message='phone_number not exists'), 200)


# 密码加密
def password_encrypt(pwd):
    return generate_password_hash(pwd)


# 验证密码
def check_password(password_hash, ckpwd):
    return check_password_hash(password_hash, ckpwd)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('check_password', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('status', type=int, required=True)
        args = parser.parse_args()
        with app.app_context():
            if args['password'] != args['check_password']:
                return make_response(jsonify(code=400, message='password not equal'), 400)
            if db.session.query(User).filter_by(name=args['name']).first():
                return make_response(jsonify(code=400, message='name already exists'), 400)
            if db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                return make_response(jsonify(code=400, message='phone_number already exists'), 400)
            else:
                # 手机号验证(待添加)
                #
                try:
                    user = User(id=id_generate(1, 1), name=args['name'],
                                password=password_encrypt(args['password']),
                                phone_number=args['phone_number'],
                                status=args['status'])
                    db.session.add(user)
                    db.session.commit()
                    return make_response(jsonify(code=200, message='success'), 200)
                except:
                    return make_response(jsonify(code=400, message='error'), 400)


def after_get_info(args, type=None):
    with app.app_context():
        # 验证用户登录信息
        if type == 'name':
            user = db.session.query(User).filter_by(name=args['name']).first()
            if user and check_password(user.password, args['password']):
                # 构建JWT负载
                payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
                           'id': user.id, 'status': user.status}
                # 生成JWT令牌
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                return make_response(jsonify(code=200, message='success', token=token, status=user.status), 200)
        if type == 'phone':
            if user := db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                # 构建JWT负载
                payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
                           'id': user.id, 'status': user.status}
                # 生成JWT令牌
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                return make_response(jsonify(code=200, message='success', token=token, status=user.status), 200)
        return make_response(jsonify(code=401, message='Invalid username or password'), 401)


# 定义用户登录接口
class Login_Name(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        return after_get_info(args, type='name')


class Login_Phone(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True)
        args = parser.parse_args()
        # 手机号验证(待添加)
        return after_get_info(args, type='phone')


def upload_photo(profile_photo):
    access_key = 'FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b'
    secret_key = 'UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9'
    bucket = 'mewstore'
    auth = qiniu.Auth(access_key, secret_key)
    uptoken = auth.upload_token(bucket)
    ret, info = qiniu.put_data(uptoken, None, profile_photo.read())
    return ret['key']


# # 定义需要JWT认证的API接口
# class User(Resource):
#     # 使用装饰器进行JWT认证和权限检查
#     @jwt_required
#     @check_status('0')
#     def get(self):
#         return
# class Black_user(Resource):
#     # 使用装饰器进行JWT认证和权限检查
#     @jwt_required
#     @check_status('1')
#     def get(self, user_id):
#         for user in users:
#             if user['id'] == user_id:
#                 return {'user': user}
#         return jsonify(code=404, message='User not found'), 404


class Users(Resource):

    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if user.profile_photo:
                    profile_photo_url = 'http://rtqcx0dtq.bkt.clouddn.com/' + user.profile_photo
                else:
                    profile_photo_url = None
                user_info = {'id': user.id, 'nickname': user.nickname, 'name': user.name,
                             'profile_photo': profile_photo_url, 'phone_number': user.phone_number,
                             'money': user.money, 'status': user.status}
                return make_response(jsonify(code=200, message='success', user=user_info), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)

    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str)
        parser.add_argument('name', type=str)
        parser.add_argument('old_password', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('check_password', type=str)
        parser.add_argument('profile_photo', type=FileStorage, location='files')
        parser.add_argument('phone_number', type=str)
        parser.add_argument('money', type=int)
        # parser.add_argument('status', type=int)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if args['old_password']:
                    if not check_password(user.password, args['old_password']):
                        return make_response(jsonify(code=400, message='old password error'), 400)
                    if args['old_password'] == args['password']:
                        return make_response(jsonify(code=400, message='new password equal old password'), 400)
                    if args['password'] != args['check_password']:
                        return make_response(jsonify(code=400, message='password not equal'), 400)
                    else:
                        user.password = password_encrypt(args['password'])
                        db.session.commit()
                        return make_response(jsonify(code=200, message='success'), 200)
                if args['nickname']:
                    if db.session.query(User).filter_by(nickname=args['nickname']).first():
                        return make_response(jsonify(code=400, message='nickname already exists'), 400)
                    else:
                        user.nickname = args['nickname']
                        db.session.commit()
                        return make_response(jsonify(code=200, message='success'), 200)
                if args['name']:
                    user.name = args['name']
                    db.session.commit()
                    return make_response(jsonify(code=200, message='success'), 200)
                if profile_photo := request.files['profile_photo']:
                    user.profile_photo = upload_photo(profile_photo)
                    db.session.commit()
                    return make_response(jsonify(code=200, message='success'), 200)
                if args['phone_number']:
                    if db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                        return make_response(jsonify(code=400, message='phone number already exists'), 400)
                    else:
                        # 手机号验证(待添加)
                        #
                        user.phone_number = args['phone_number']
                        db.session.commit()
                        return make_response(jsonify(code=200, message='success'), 200)
                if args['money']:
                    # 金额验证(待添加)
                    #
                    user.money = args['money']
                    db.session.commit()
                    return make_response(jsonify(code=200, message='success'), 200)
                # if args['status']:
                #     self.user.status = args['status']
                #     data.session.commit()
                #     return jsonify(code=200, message='success'), 200
                else:
                    return make_response(jsonify(code=400, message='error'), 400)
            else:
                return make_response(jsonify(code=400, message='error'), 400)

    # # 使用装饰器进行JWT认证和权限检查
    # @jwt_required(lambda payload: request.jwt_payload['status'] == '1')


class Black_user(Resource):

    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 1:
                user_info = {'id': user.id, 'nickname': user.nickname, 'name': user.name,
                             'profile_photo': user.profile_photo, 'phone_number': user.phone_number,
                             'money': user.money, 'status': user.status}
                return make_response(jsonify(code=200, message='success', user=user_info), 200)

    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('money', type=int)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 1:
                if args['money']:
                    # 金额验证(待添加)
                    #
                    user.money = args['money']
                    db.session.commit()
                    return make_response(jsonify(code=200, message='success'), 200)


class Frozen_user(Resource):

    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
        if user and user.status == 2:
            user_info = {'id': user.id, 'nickname': user.nickname, 'name': user.name,
                         'profile_photo': user.profile_photo, 'phone_number': user.phone_number,
                         'money': user.money, 'status': user.status}
            return make_response(jsonify(code=200, message='success', user=user_info), 200)


# 添加API接口路由
api.add_resource(Register, '/register')
api.add_resource(Login_Name, '/login/name')
api.add_resource(Login_Phone, '/login/phone')
api.add_resource(Users, '/user')
api.add_resource(Black_user, '/user/black')
api.add_resource(Frozen_user, '/user/frozen')
api.add_resource(Sms, '/sms')