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


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('check_password', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('status', type=int, required=True)
        args = parser.parse_args()
        with app.app_context():
            if args['password'] != args['check_password']:
                return make_response(jsonify(code=400, message='password not equal'), 400)
            if db.session.query(User).filter_by(username=args['username']).first():
                return make_response(jsonify(code=400, message='username already exists'), 400)
            if len(args['phone_number']) != 11:
                return make_response(jsonify(code=400, message='phone_number error'), 400)
            if db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                return make_response(jsonify(code=400, message='phone_number already exists'), 400)
            else:
                # 手机号验证(待添加)
                #
                try:
                    user = User(id=id_generate(1, 1), username=args['username'],
                                password=generate_password_hash(args['password']),
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
        if type == 'username':
            user = db.session.query(User).filter_by(username=args['username']).first()
            if user and check_password_hash(user.password, args['password']):
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
class Login_Username(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        return after_get_info(args, type='username')


class Login_Phone(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True)
        args = parser.parse_args()
        # 手机号验证(待添加)
        return after_get_info(args, type='phone')


def upload_photo(photo):
    access_key = 'FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b'
    secret_key = 'UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9'
    bucket = 'mewstore'
    auth = qiniu.Auth(access_key, secret_key)
    uptoken = auth.upload_token(bucket)
    ret, info = qiniu.put_data(uptoken, None, photo.read())
    return ret['key']


def delete_photo(photo):
    access_key = 'FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b'
    secret_key = 'UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9'
    bucket_name = 'mewstore'
    auth = qiniu.Auth(access_key, secret_key)
    bucket = qiniu.BucketManager(auth)
    bucket.delete(bucket_name, photo)
    return True


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


class User_get(Resource):
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
                user_info = {'id': user.id, 'nickname': user.nickname, 'username': user.username,
                             'profile_photo': profile_photo_url, 'phone_number': user.phone_number,
                             'money': user.money, 'status': user.status, 'name': user.name, 'id_card': user.id_card}
                return make_response(jsonify(code=200, message='success', user=user_info), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class User_nickname(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                user.nickname = args['nickname']
                db.session.commit()
                return make_response(jsonify(code=200, message='success'), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class User_username(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if db.session.query(User).filter(User.username == args['username']).first():
                    return make_response(jsonify(code=400, message='The username has already been used'), 400)
                user.username = args['username']
                db.session.commit()
                return make_response(jsonify(code=200, message='success'), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class User_password(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('old_password', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('check_password', type=str, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if check_password_hash(user.password, args['old_password']):
                    if args['password'] == args['check_password']:
                        user.password = generate_password_hash(args['password'])
                        db.session.commit()
                        return make_response(jsonify(code=200, message='success'), 200)
                    else:
                        return make_response(jsonify(code=400, message='error'), 400)
                else:
                    return make_response(jsonify(code=400, message='error'), 400)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class User_profile_photo(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('profile_photo', type=FileStorage, location=['files'], required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if user.profile_photo:
                    delete_photo(user.profile_photo)
                user.profile_photo = upload_photo(args['profile_photo'])
                db.session.commit()
                return make_response(jsonify(code=200, message='success'), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class User_phone_number(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if db.session.query(User).filter(User.phone_number == args['phone_number']).first():
                    return make_response(jsonify(code=400, message='The phone number has already been used'), 400)
                # 手机号验证
                user.phone_number = args['phone_number']
                db.session.commit()
                return make_response(jsonify(code=200, message='success'), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class User_money(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('money', type=int, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                user.money = args['money']
                db.session.commit()
                return make_response(jsonify(code=200, message='success'), 200)
            else:
                return make_response(jsonify(code=400, message='error'), 400)


class Black_user(Resource):
    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 1:
                user_info = {'id': user.id, 'nickname': user.nickname, 'username': user.username,
                             'profile_photo': user.profile_photo, 'phone_number': user.phone_number,
                             'money': user.money, 'status': user.status, 'name': user.name, 'id_card': user.id_card}
                return make_response(jsonify(code=200, message='success', user=user_info), 200)


class Black_money(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('money', type=int, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 1:
                if args['money']:
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
            user_info = {'id': user.id, 'nickname': user.nickname, 'username': user.username,
                         'profile_photo': user.profile_photo, 'phone_number': user.phone_number,
                         'money': user.money, 'status': user.status, 'name': user.name, 'id_card': user.id_card}
            return make_response(jsonify(code=200, message='success', user=user_info), 200)


# 添加API接口路由
api.add_resource(Register, '/register')
api.add_resource(Login_Username, '/login/name')
api.add_resource(Login_Phone, '/login/phone')
api.add_resource(User_get, '/user')
api.add_resource(User_nickname, '/user/nickname')
api.add_resource(User_username, '/user/username')
api.add_resource(User_password, '/user/password')
api.add_resource(User_profile_photo, '/user/profile_photo')
api.add_resource(User_phone_number, '/user/phone_number')
api.add_resource(User_money, '/user/money')
api.add_resource(Black_user, '/user/black')
api.add_resource(Black_money, '/user/black/money')
api.add_resource(Frozen_user, '/user/frozen')
api.add_resource(Sms, '/sms')
