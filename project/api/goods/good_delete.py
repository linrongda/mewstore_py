from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import User, db, Good
from project.utils.auth import jwt_required
from project.utils.log import logger


class Good_delete(Resource):
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='商品id不能为空')
        id = parser.parse_args().get('id')
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            # 查询
            good = db.session.query(Good).get(id)
            # 判断是否存在
            if not good or good.seller_id != user.id:
                return make_response(jsonify(code=404, message='商品不存在'), 404)
            # 删除商品
            db.session.delete(good)
            # 提交修改
            db.session.commit()
            logger.debug('删除商品成功')
            # 返回结果
            return make_response(jsonify(code=204, message='删除商品成功'), 204)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
