import re

from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash

from project.exts import redis
from project.models import User, db
from project.utils.aes import encrypt
from project.utils.log import logger
from project.utils.snowflake import id_generate


class Register(Resource):  # 注册
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        parser.add_argument('password', type=str, required=True, help='请输入密码')
        parser.add_argument('check_password', type=str, required=True, help='请输入确认密码')
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('code', type=str, required=True, help='请输入验证码')
        args = parser.parse_args()
        if args['password'] != args['check_password']:
            return make_response(jsonify(code=400, message='两次输入的密码不一致'), 400)
        if db.session.query(User).filter_by(username=args['username']).first():
            return make_response(jsonify(code=400, message='用户名已存在'), 400)
        if not bool(re.match(r'^1[3-9]\d{9}$', args['phone_number'])):
            return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
        if db.session.query(User).filter_by(phone_number=encrypt(args['phone_number'])).first():
            return make_response(jsonify(code=400, message='手机号已存在'), 400)
        if not redis.get(f'{args["phone_number"]}'):
            return make_response(jsonify(code=400, message='请先获取验证码'), 400)
        if args['code'] != redis.get(f'{args["phone_number"]}'):
            return make_response(jsonify(code=400, message='验证码错误'), 400)
        else:
            try:
                user = User(id=id_generate('user'), username=args['username'], nickname='默认昵称', status=0,
                            password=generate_password_hash(args['password']), money=0,
                            phone_number=encrypt(args['phone_number']),
                            profile_photo='http://qiniuyun.mewtopia.cn/Fuo2xUtkCE3MHDj87R3nqMpmMm5W')  # 使用雪花算法生成id，密码使用hash加密，status=0表示普通用户
                db.session.add(user)
                db.session.commit()
                logger.debug(f'用户{args["username"]}注册成功')
                return make_response(jsonify(code=201, message='注册成功'), 201)
            except Exception as e:
                return make_response(jsonify(code=400, message=f'发生未知错误：{e}'), 400)
