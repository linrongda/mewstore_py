from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import db, Good
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Good_delete(Resource):  # 删除商品
    @jwt_required
    @check_status([0, 3])
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='商品id不能为空')
        good_id = parser.parse_args().get('id')
        user = request.user
        # 查询
        good = db.session.query(Good).get(good_id)
        # 判断是否存在
        if not good or good.seller_id != user.id:
            return make_response(jsonify(code=404, message='商品不存在'), 404)
        # 删除商品
        db.session.delete(good)
        # 提交修改
        db.session.commit()
        logger.debug(f'用户{user.username}删除商品{good_id}成功')
        # 返回结果
        return make_response(jsonify(code=204, message='删除商品成功'), 204)
