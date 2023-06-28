from flask import make_response, jsonify, request
from flask_restful import Resource

from project.models import Good, db, User
from project.utils.Time_Transform import time_transform
from project.utils.log import logger


class Good_get(Resource):  # 获取商品信息
    def get(self):
        good_id = request.args.get('id', type=int)
        # 查询
        good = db.session.query(Good).get(good_id)
        # 判断是否存在
        if not good:
            return make_response(jsonify(code=404, message='商品不存在'), 404)
        # 获取商品信息
        else:
            seller = db.session.query(User).get(good.seller_id)
            good_info = {'id': str(good.id), 'view': good.view, 'game': good.game, 'picture_url': good.picture,
                         'title': good.title, 'content': good.content, 'add_time': time_transform(good.add_time),
                         'status': good.status, 'seller_id': str(good.seller_id), 'price': good.price,
                         'seller_nickname': seller.nickname, 'seller_profile_photo': seller.profile_photo}
            logger.debug(f'获取商品{good.id}信息成功')
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品信息成功', data=good_info), 200)
