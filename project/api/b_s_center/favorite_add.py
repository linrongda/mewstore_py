from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import User, db, Favorite, Good
from project.utils.auth import jwt_required
from project.utils.log import logger


class Favorite_add(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('good_id', type=int, required=True, help='商品id必须提供')
        args = parser.parse_args()
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
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
                logger.debug('收藏成功')
                # 返回结果
                return make_response(jsonify(code=201, message='收藏成功'), 201)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
