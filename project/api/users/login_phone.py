import datetime
import re

from flask import make_response, jsonify, session
from flask_restful import Resource, reqparse

from project.utils.auth import after_get_info


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
        if session[f'{args["phone_number"]}_time'] + datetime.timedelta(minutes=4) < datetime.datetime.utcnow():
            return make_response(jsonify(code=400, message='验证码已过期'), 400)
        else:
            return after_get_info(args, login_type='phone')
