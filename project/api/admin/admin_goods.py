from flask import make_response, jsonify
from flask_restful import Resource

from project.models import db, Good, User
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Admin_goods(Resource):  # 管理员获取不同状态商品
    @jwt_required
    @check_status([3])
    def get(self):
        # 查询
        goods = db.session.query(Good).all()
        if not goods:
            return make_response(jsonify(code=404, message='找不到有关的商品'), 404)
        good_list = []
        for good in goods:
            seller = db.session.query(User).get(good.seller_id)
            good_dict = {"id": str(good.id), "view": good.view, "content": good.content, "game": good.game,
                         "title": good.title, "picture_url": good.picture, "status": good.status,
                         'add_time': time_transform(good.add_time), "seller_id": str(good.seller_id),
                         "price": good.price, 'seller_nickname': seller.nickname,
                         'seller_profile_photo': seller.profile_photo}
            good_list.append(good_dict)
        logger.debug(f'管理员获取商品成功')
        # 返回结果
        return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)
