from flask import make_response, jsonify, request
from flask_restful import Resource, reqparse

from project.models import db
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class User_money(Resource):  # 修改用户金额
    @jwt_required
    @check_status([0, 1, 3])
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('money', type=int, required=True, help='请输入金额')
        parser.add_argument('type', type=str, required=True, help='请输入修改类型')
        args = parser.parse_args()
        if args['type'] not in ('recharge', 'withdrawal'):
            return make_response(jsonify(code=400, message='type参数错误'), 400)
        user = request.user
        if user.money is None:
            user.money = 0
        if args['type'] == 'recharge':
            if args['money'] < 0:
                return make_response(jsonify(code=400, message='充值金额不能为负数'), 400)
            user.money += args['money']
            db.session.commit()
            logger.debug(f'用户{user.username}充值成功')
            return make_response(jsonify(code=201, message='充值成功', data={'money': user.money}), 201)
        if args['type'] == 'withdrawal':
            if user.money >= args['money']:
                user.money -= args['money']
                db.session.commit()
                logger.debug(f'用户{user.username}提现成功')
                return make_response(jsonify(code=201, message='提现成功', data={'money': user.money}), 201)
            else:
                return make_response(jsonify(code=400, message='余额不足'), 400)
