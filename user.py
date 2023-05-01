import datetime
import logging
import random

import jwt
import qiniu
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from flask import request, jsonify, Blueprint, make_response, session
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash

from api.data import User, db, app
from api.sendsms import Sample
from api.snowflake import id_generate

# 定义应用和API
user = Blueprint('user', __name__)
api = Api(user)

logger = logging.getLogger(__name__)

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
                logger.debug('解析token成功')
                request.jwt_payload = payload
                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return make_response(jsonify(code=401, message='登录信息过期'), 401)
            except jwt.InvalidTokenError:
                return make_response(jsonify(code=401, message='非法登录'), 401)
        else:
            return make_response(jsonify(code=401, message='找不到登录信息'), 401)

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
                return make_response(jsonify(code=400, message='该手机号已存在'), 400)
            if session[f'{phone_number}'] and session[f'{phone_number}_time'] > datetime.datetime.now():
                return make_response(jsonify(code=400, message='请勿重复发送验证码'), 400)
            else:
                code = ''.join(random.choices('0123456789', k=6))
                client = Sample.create_client(access_key_id='LTAI5tNVqQ16EgH2Xn6fxar1',
                                              access_key_secret='eIm61r1Uy8e5IDjDepBN3JKiqXmLeO')
                send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
                    sign_name='闲猫MewStore',
                    template_code='SMS_460685295',
                    phone_numbers=phone_number,
                    template_param='{"code":"%s"}' % code
                )
                runtime = util_models.RuntimeOptions()
                try:
                    # 复制代码运行请自行打印 API 的返回值
                    response = client.send_sms_with_options(send_sms_request, runtime)
                    print(response)
                    if response.body.code == 'OK':
                        session[f'{phone_number}'] = code
                        session[f'{phone_number}_time'] = datetime.datetime.now()+datetime.timedelta(minutes=1)
                        logger.debug('发送验证码成功')
                        return make_response(jsonify(code=200, message='发送成功'), 200)
                    else:
                        return make_response(jsonify(code=200, message='发送失败'), 200)
                except Exception as error:
                    # 如有需要，请打印 error
                    # UtilClient.assert_as_string(error.message)
                    return make_response(jsonify(code=400, message=f'发生未知错误：{error}'), 400)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('check_password', type=str, required=True)
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('status', type=int, required=True)
        parser.add_argument('code', type=str, required=True)
        args = parser.parse_args()
        with app.app_context():
            if args['password'] != args['check_password']:
                return make_response(jsonify(code=400, message='两次输入的密码不一致'), 400)
            if db.session.query(User).filter_by(username=args['username']).first():
                return make_response(jsonify(code=400, message='用户名已存在'), 400)
            if len(args['phone_number']) != 11:
                return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
            if db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                return make_response(jsonify(code=400, message='手机号已存在'), 400)
            if args['code'] != session[f'{args["phone_number"]}']:
                return make_response(jsonify(code=400, message='验证码错误'), 400)
            else:
                try:
                    user = User(id=id_generate(1, 1), username=args['username'],
                                password=generate_password_hash(args['password']),
                                phone_number=args['phone_number'],
                                status=args['status'])
                    db.session.add(user)
                    db.session.commit()
                    logger.debug('注册成功')
                    return make_response(jsonify(code=201, message='注册成功'), 201)
                except Exception as e:
                    return make_response(jsonify(code=400, message=f'发生未知错误：{e}'), 400)


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
                logger.debug('登录成功')
                return make_response(jsonify(code=200, message='登录成功', token=token, status=user.status), 200)
            return make_response(jsonify(code=401, message='用户名或密码错误'), 401)
        if type == 'phone':
            if user := db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                # 构建JWT负载
                payload = {'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA, 'iat': datetime.datetime.utcnow(),
                           'id': user.id, 'status': user.status}
                # 生成JWT令牌
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
                logger.debug('登录成功')
                return make_response(jsonify(code=200, message='登录成功', token=token, status=user.status), 200)
            return make_response(jsonify(code=401, message='用户不存在'), 401)
        else:
            return make_response(jsonify(code=400, message='请求参数错误'), 400)


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
        parser.add_argument('code', type=str, required=True)
        args = parser.parse_args()
        if args['code'] != session[f'{args["phone_number"]}']:
            return make_response(jsonify(code=400, message='验证码错误'), 400)
        else:
            return after_get_info(args, type='phone')


def upload_photo(photo):
    access_key = 'FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b'
    secret_key = 'UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9'
    bucket = 'mewstore'
    auth = qiniu.Auth(access_key, secret_key)
    uptoken = auth.upload_token(bucket)
    ret, info = qiniu.put_data(uptoken, None, photo.read())
    return ret['key']


# def delete_photo(photo):
#     access_key = 'FU5sKsfrD422VmfLSxCm6AxnjNHxUA_VYf1xdT1b'
#     secret_key = 'UfRIgz3x0Vt7reIdbZxe_HAX-pwjbg2sqkPHoUq9'
#     bucket_name = 'mewstore'
#     auth = qiniu.Auth(access_key, secret_key)
#     bucket = qiniu.BucketManager(auth)
#     bucket.delete(bucket_name, photo)
#     return True


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
                logger.debug('获取用户信息成功')
                return make_response(jsonify(code=200, message='获取用户信息成功', user=user_info), 200)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
                logger.debug('修改昵称成功')
                return make_response(jsonify(code=201, message='修改昵称成功'), 201)
            else:
                return make_response(jsonify(code=403, message='error'), 403)


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
                    return make_response(jsonify(code=400, message='该用户名已存在'), 400)
                user.username = args['username']
                db.session.commit()
                logger.debug('修改用户名成功')
                return make_response(jsonify(code=201, message='修改用户名成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
                        logger.debug('修改密码成功')
                        return make_response(jsonify(code=201, message='修改密码成功'), 201)
                    else:
                        return make_response(jsonify(code=400, message='两次输入的密码不一致'), 400)
                else:
                    return make_response(jsonify(code=401, message='原密码错误'), 401)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
                # if user.profile_photo:
                #     delete_photo(user.profile_photo)
                user.profile_photo = upload_photo(args['profile_photo'])
                db.session.commit()
                logger.debug('修改头像成功')
                return make_response(jsonify(code=201, message='修改头像成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


class User_phone_number(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True)
        parser.add_argument('code', type=str, required=True)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                if db.session.query(User).filter(User.phone_number == args['phone_number']).first():
                    return make_response(jsonify(code=400, message='该手机号已存在'), 400)
                if args['code'] != session[f'{args["phone_number"]}']:
                    return make_response(jsonify(code=400, message='验证码错误'), 400)
                user.phone_number = args['phone_number']
                db.session.commit()
                logger.debug('修改手机号成功')
                return make_response(jsonify(code=201, message='修改手机号成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
                logger.debug('修改余额成功')
                return make_response(jsonify(code=201, message='修改余额成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
                logger.debug('获取用户信息成功')
                return make_response(jsonify(code=200, message='获取用户信息成功', user=user_info), 200)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
                user.money = args['money']
                db.session.commit()
                logger.debug('修改余额成功')
                return make_response(jsonify(code=201, message='修改余额成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


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
            logger.debug('获取用户信息成功')
            return make_response(jsonify(code=200, message='获取用户信息成功', user=user_info), 200)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)


# 添加API接口路由
api.add_resource(Register, '/users')
api.add_resource(Login_Username, '/login/username')
api.add_resource(Login_Phone, '/login/phone')
api.add_resource(User_get, '/users')
api.add_resource(User_nickname, '/users/nickname')
api.add_resource(User_username, '/users/username')
api.add_resource(User_password, '/users/password')
api.add_resource(User_profile_photo, '/users/profile-photo')
api.add_resource(User_phone_number, '/users/phone-number')
api.add_resource(User_money, '/users/money')
api.add_resource(Black_user, '/blacks')
api.add_resource(Black_money, '/blacks/money')
api.add_resource(Frozen_user, '/frozen')
api.add_resource(Sms, '/sms/<int:phone_number>')
