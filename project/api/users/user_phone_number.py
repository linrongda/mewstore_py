import datetime
import re

from flask import request, make_response, jsonify, session
from flask_restful import Resource, reqparse

from project.models import User, db
from project.utils.auth import jwt_required
from project.utils.log import logger


class User_phone_number(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('code', type=str, required=True, help='请输入验证码')
        args = parser.parse_args()
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            if not bool(re.match(r'^1[3-9]\d{9}$', args['phone_number'])):
                return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
            if db.session.query(User).filter(User.phone_number == args['phone_number']).first():
                return make_response(jsonify(code=400, message='该手机号已被使用'), 400)
            if not session.get(f'{args["phone_number"]}_time') or not session.get(f'{args["phone_number"]}'):
                return make_response(jsonify(code=400, message='请先获取验证码'), 400)
            if args['code'] != session[f'{args["phone_number"]}']:
                return make_response(jsonify(code=400, message='验证码错误'), 400)
            if session[f'{args["phone_number"]}_time'] + datetime.timedelta(minutes=4) < datetime.datetime.utcnow():
                return make_response(jsonify(code=400, message='验证码已过期'), 400)
            user.phone_number = args['phone_number']
            db.session.commit()
            logger.debug('修改手机号成功')
            return make_response(jsonify(code=201, message='修改手机号成功'), 201)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
