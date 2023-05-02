import datetime
import json
import logging
import random
import re

import jwt
import qiniu
import requests
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


class Sms(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('type', type=str, required=True, help='请输入验证类型')
        args = parser.parse_args()
        if args['type'] not in ['register', 'login', 'modify']:
            return make_response(jsonify(code=400, message='type参数错误'), 400)
        if not bool(re.match(r'^1[3-9]\d{9}$', args['phone_number'])):
            return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
        with app.app_context():
            if args['type'] == 'register':
                if User.query.filter_by(phone_number=args['phone_number']).first():
                    return make_response(jsonify(code=400, message='该手机号已被注册'), 400)
            if args['type'] == 'login':
                if not db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                    return make_response(jsonify(code=404, message='用户不存在'), 404)
            if args['type'] == 'modify':
                if User.query.filter_by(phone_number=args['phone_number']).first():
                    return make_response(jsonify(code=400, message='该手机号已被使用'), 400)
            if session.get(f'{args["phone_number"]}') and session[
                f'{args["phone_number"]}_time'] > datetime.datetime.now():
                return make_response(jsonify(code=400, message='请勿重复发送验证码'), 400)
            else:
                code = ''.join(random.choices('0123456789', k=6))
                client = Sample.create_client(access_key_id='LTAI5tNVqQ16EgH2Xn6fxar1',
                                              access_key_secret='eIm61r1Uy8e5IDjDepBN3JKiqXmLeO')
                send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
                    sign_name='闲猫MewStore',
                    template_code='SMS_460685295',
                    phone_numbers=args["phone_number"],
                    template_param='{"code":"%s"}' % code
                )
                runtime = util_models.RuntimeOptions()
                try:
                    # 复制代码运行请自行打印 API 的返回值
                    response = client.send_sms_with_options(send_sms_request, runtime)
                    print(response)
                    if response.body.code == 'OK':
                        session[f'{args["phone_number"]}'] = code
                        session[f'{args["phone_number"]}_time'] = datetime.datetime.now() + datetime.timedelta(
                            minutes=1)
                        logger.debug('发送验证码成功')
                        return make_response(jsonify(code=200, message='发送成功'), 200)
                    else:
                        return make_response(jsonify(code=400, message='发送失败'), 400)
                except Exception as error:
                    # 如有需要，请打印 error
                    # UtilClient.assert_as_string(error.message)
                    return make_response(jsonify(code=400, message=f'发生未知错误：{error}'), 400)


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        parser.add_argument('password', type=str, required=True, help='请输入密码')
        parser.add_argument('check_password', type=str, required=True, help='请输入确认密码')
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('status', type=int, required=True, help='请输入用户状态')
        parser.add_argument('code', type=str, required=True, help='请输入验证码')
        args = parser.parse_args()
        with app.app_context():
            if args['password'] != args['check_password']:
                return make_response(jsonify(code=400, message='两次输入的密码不一致'), 400)
            if db.session.query(User).filter_by(username=args['username']).first():
                return make_response(jsonify(code=400, message='用户名已存在'), 400)
            if not bool(re.match(r'^1[3-9]\d{9}$', args['phone_number'])):
                return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
            if db.session.query(User).filter_by(phone_number=args['phone_number']).first():
                return make_response(jsonify(code=400, message='手机号已存在'), 400)
            if not session.get(f'{args["phone_number"]}_time') or not session.get(f'{args["phone_number"]}'):
                return make_response(jsonify(code=400, message='请先获取验证码'), 400)
            if args['code'] != session[f'{args["phone_number"]}']:
                return make_response(jsonify(code=400, message='验证码错误'), 400)
            if session[f'{args["phone_number"]}_time'] + datetime.timedelta(minutes=4) < datetime.datetime.now():
                return make_response(jsonify(code=400, message='验证码已过期'), 400)
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
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        parser.add_argument('password', type=str, required=True, help='请输入密码')
        args = parser.parse_args()
        return after_get_info(args, type='username')


class Login_Phone(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('code', type=str, required=True, help='请输入验证码')
        args = parser.parse_args()
        if not bool(re.match(r'^1[3-9]\d{9}$', args['phone_number'])):
            return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
        if not session.get(f'{args["phone_number"]}_time') or not session.get(f'{args["phone_number"]}'):
            return make_response(jsonify(code=400, message='请先获取验证码'), 400)
        if args['code'] != session[f'{args["phone_number"]}']:
            return make_response(jsonify(code=400, message='验证码错误'), 400)
        if session[f'{args["phone_number"]}_time'] + datetime.timedelta(minutes=4) < datetime.datetime.now():
            return make_response(jsonify(code=400, message='验证码已过期'), 400)
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

def r_n_a(name, id_card):
    url = 'http://eid.shumaidata.com/eid/check'
    params = {
        'idcard': id_card,
        'name': name
    }
    headers = {
        'Authorization': 'APPCODE 7740e015b9c1430b9c74d592f1153bdb'
    }
    # 发送请求并获取响应
    response = requests.post(url, params=params, headers=headers)
    # 解析响应并返回结果
    result = json.loads(response.text)
    if result['result']['res'] == '1':
        return True
    else:
        return False


class User_get(Resource):
    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in range(0, 4):
                if user.profile_photo:
                    profile_photo_url = 'http://rtqcx0dtq.bkt.clouddn.com/' + user.profile_photo
                else:
                    profile_photo_url = None
                    name = user.name[0] + '*' * (len(user.name) - 1) if user.name else None
                    id_card = user.id_card[0] + '*' * (len(user.id_card) - 2) + user.id_card[
                        -1] if user.id_card else None
                user_info = {'id': user.id, 'nickname': user.nickname, 'username': user.username,
                             'profile_photo': profile_photo_url, 'phone_number': user.phone_number,
                             'money': user.money, 'status': user.status, 'name': name, 'id_card': id_card}
                logger.debug('获取用户信息成功')
                return make_response(jsonify(code=200, message='获取用户信息成功', user=user_info), 200)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


class User_nickname(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True, help='请输入昵称')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
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
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
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
        parser.add_argument('old_password', type=str, required=True, help='请输入原密码')
        parser.add_argument('password', type=str, required=True, help='请输入新密码')
        parser.add_argument('check_password', type=str, required=True, help='请输入确认密码')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
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
        parser.add_argument('profile_photo', type=FileStorage, location=['files'], required=True, help='请上传头像')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
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
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('code', type=str, required=True, help='请输入验证码')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
                if db.session.query(User).filter(User.phone_number == args['phone_number']).first():
                    return make_response(jsonify(code=400, message='该手机号已被使用'), 400)
                if not session.get(f'{args["phone_number"]}_time') or not session.get(f'{args["phone_number"]}'):
                    return make_response(jsonify(code=400, message='请先获取验证码'), 400)
                if args['code'] != session[f'{args["phone_number"]}']:
                    return make_response(jsonify(code=400, message='验证码错误'), 400)
                if session[f'{args["phone_number"]}_time'] + datetime.timedelta(minutes=4) < datetime.datetime.now():
                    return make_response(jsonify(code=400, message='验证码已过期'), 400)
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
        parser.add_argument('money', type=int, required=True, help='请输入金额')
        parser.add_argument('type', type=str, required=True, help='请输入修改类型')
        args = parser.parse_args()
        if args['type'] not in ('recharge', 'withdrawal'):
            return make_response(jsonify(code=400, message='type参数错误'), 400)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 1, 3):
                if user.money is None:
                    user.money = 0
                if args['type'] == 'recharge':
                    if args['money'] < 0:
                        return make_response(jsonify(code=400, message='充值金额不能为负数'), 400)
                    user.money += args['money']
                    db.session.commit()
                    logger.debug('充值成功')
                    return make_response(jsonify(code=201, message='充值成功'), 201)
                if args['type'] == 'withdrawal':
                    if user.money >= args['money']:
                        user.money -= args['money']
                        db.session.commit()
                        logger.debug('提现成功')
                        return make_response(jsonify(code=201, message='提现成功'), 201)
                    else:
                        return make_response(jsonify(code=400, message='余额不足'), 400)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


class Real_name_authentication(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='请输入姓名')
        parser.add_argument('id_card', type=str, required=True, help='请输入身份证号')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
                if user.name and user.id_card:
                    return make_response(jsonify(code=400, message='你已经实名认证过了'), 400)
                if db.session.query(User).filter_by(name=args['name'], id_card=args['id_card']).first():
                    return make_response(jsonify(code=400, message='该身份证已被使用'), 400)
                if session.get(f'{user_id}_time') and session[f'{user_id}_time'] > datetime.datetime.now():
                    return make_response(jsonify(code=400, message='请勿重复提交'), 400)
                session[f'{user_id}_time'] = datetime.datetime.now() + datetime.timedelta(days=90)
                if r_n_a(args['name'], args['id_card']):
                    user.name = args['name']
                    user.id_card = args['id_card']
                    db.session.commit()
                    logger.debug('实名认证成功')
                    return make_response(jsonify(code=201, message='实名认证成功'), 201)
                else:
                    return make_response(jsonify(code=400, message='实名认证失败'), 400)
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
api.add_resource(Real_name_authentication, '/users/real-name-authentication')
api.add_resource(Sms, '/sms')
