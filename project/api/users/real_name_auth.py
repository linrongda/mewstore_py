import datetime
import re

from flask import request, make_response, jsonify, session
from flask_restful import Resource, reqparse

from project.models import User, db
from project.utils.R_N_A import r_n_a
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Real_name_authentication(Resource):  # 实名认证
    @jwt_required
    @check_status([0, 3])
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='请输入姓名')
        parser.add_argument('id_card', type=str, required=True, help='请输入身份证号')
        args = parser.parse_args()
        user = request.user
        user_id = user.id
        if not bool(re.match(r'^[1-9]\d{5}(19\d{2}|2\d{3})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$',
                             args['id_card'])):
            return make_response(jsonify(code=400, message='请输入18位正确的身份证号'), 400)
        if user.name and user.id_card:
            return make_response(jsonify(code=400, message='你已经实名认证过了'), 400)
        if db.session.query(User).filter_by(name=args['name'], id_card=args['id_card']).first():
            return make_response(jsonify(code=400, message='该身份证已被使用'), 400)
        if session.get(f'{user_id}_time') and \
                session[f'{user_id}_time'].replace(tzinfo=None) > datetime.datetime.utcnow():
            return make_response(jsonify(code=400, message='请勿重复提交'), 400)
        session[f'{user_id}_time'] = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        # if r_n_a(args['name'], args['id_card']):
        #     user.name = args['name']
        #     user.id_card = args['id_card']
        #     db.session.commit()
        #     logger.debug(f'用户{user.username}实名认证成功')
        #     name = '*' * (len(user.name) - 1) + user.name[-1] if user.name else None
        #     id_card = user.id_card[0] + '*' * (len(user.id_card) - 2) + user.id_card[-1] if user.id_card else None
        #     return make_response(jsonify(code=201, message='实名认证成功',data={'name':name,'id_card':id_card}), 201)
        # else:
        return make_response(jsonify(code=400, message='实名认证失败'), 400)
