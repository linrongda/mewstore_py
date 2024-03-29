from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import db, Good
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Sell(Resource):  # 用户查询出售商品
    @jwt_required
    @check_status([0, 3])
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        user = request.user
        # 查询
        sql_goods = db.session.query(Good).filter_by(seller_id=user.id)
        goods = sql_goods.paginate(page=page, per_page=size).items
        good_list = []
        for good in goods:
            good_dict = {'id': str(good.id), 'view': good.view, 'game': good.game, 'title': good.title,
                         'content': good.content, 'picture_url': good.picture,
                         'add_time': time_transform(good.add_time),
                         'status': good.status, 'seller_id': str(good.seller_id), 'price': good.price}
            good_list.append(good_dict)
        logger.debug(f'用户{user.username}获取出售商品成功')
        # 返回结果
        return make_response(jsonify(code=200, message='获取出售商品成功', data=good_list), 200)
