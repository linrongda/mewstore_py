from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import db, Favorite, Good
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Favorite_add(Resource):  # 用户添加收藏
    @jwt_required
    @check_status([0, 3])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('good_id', type=int, required=True, help='商品id必须提供')
        args = parser.parse_args()
        user = request.user
        # 查询
        favorite = db.session.query(Favorite).filter_by(user_id=user.id, good_id=args['good_id']).first()
        if favorite:
            return make_response(jsonify(code=400, message='已收藏'), 400)
        good = db.session.query(Good).get(args['good_id'])
        if not good:
            return make_response(jsonify(code=404, message='商品不存在'), 404)
        else:
            # 添加
            favorite = Favorite(user_id=user.id, good_id=args['good_id'])
            db.session.add(favorite)
            good.view += 1
            db.session.commit()
            logger.debug(f'用户{user.username}收藏商品{good.id}成功')
            # 返回结果
            return make_response(jsonify(code=201, message='收藏成功'), 201)
