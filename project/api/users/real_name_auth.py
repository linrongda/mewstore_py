import datetime
import re

from flask import request, make_response, jsonify, session
from flask_restful import Resource, reqparse

from project.app import app
from project.models import User, db
from project.utils.R_N_A import r_n_a
from project.utils.auth import jwt_required
from project.utils.log import logger


class Real_name_authentication(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='请输入姓名')
        parser.add_argument('id_card', type=str, required=True, help='请输入身份证号')
        args = parser.parse_args()
        user_id = request.payload_id
        # with app.app_context():
        user = db.session.query(User).get(user_id)
        if user and user.status in (0, 3):
            if not bool(re.match(r'^[1-9]\d{5}(19\d{2}|2\d{3})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$',
                                 args['id_card'])):
                return make_response(jsonify(code=400, message='请输入18位正确的身份证号'), 400)
            if user.name and user.id_card:
                return make_response(jsonify(code=400, message='你已经实名认证过了'), 400)
            if db.session.query(User).filter_by(name=args['name'], id_card=args['id_card']).first():
                return make_response(jsonify(code=400, message='该身份证已被使用'), 400)
            if session.get(f'{user_id}_time') and \
                    session[f'{user_id}_time'] > datetime.datetime.utcnow():
                return make_response(jsonify(code=400, message='请勿重复提交'), 400)
            session[f'{user_id}_time'] = datetime.datetime.utcnow() + datetime.timedelta(days=90)
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