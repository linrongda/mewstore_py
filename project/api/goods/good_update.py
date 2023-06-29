from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import db, Good
from project.utils.aes import encrypt
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Good_update(Resource):  # 修改商品信息
    @jwt_required
    @check_status([0, 3])
    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, location=['form'], help='商品id不能为空')
        parser.add_argument('game', type=str, location=['form'])
        parser.add_argument('title', type=str, location=['form'])
        parser.add_argument('content', type=str, location=['form'])
        parser.add_argument('picture', type=str, location=['form'])
        parser.add_argument('account', type=str, location=['form'])
        parser.add_argument('password', type=str, location=['form'])
        parser.add_argument('status', type=int, location=['form'])
        parser.add_argument('price', type=float, location=['form'])
        args = parser.parse_args()
        user = request.user
        # 查询
        good = db.session.query(Good).get(args['id'])
        # 判断是否存在
        if not good or good.seller_id != user.id:
            return make_response(jsonify(code=404, message='商品不存在'), 404)
        # 修改商品信息
        if args['game']:
            good.game = args['game']
        if args['content']:
            good.content = args['content']
        if args['title']:
            good.title = args['title']
        if args['picture']:  # 此处不能删除照片，防止有人的头像或商品图是这里的商品图（有可能），从而把头像删了
            good.picture = args['picture']
        if args['account']:
            good.account = args['account']
        if args['password']:
            good.password = encrypt(args['password'])
        if args['status']:
            good.status = args['status']
        if args['price']:
            good.price = args['price']
        # 提交修改
        db.session.commit()
        logger.debug(f'用户{user.username}修改商品{good.id}信息成功')
        # 返回结果
        return make_response(jsonify(code=201, message='修改商品信息成功'), 201)
