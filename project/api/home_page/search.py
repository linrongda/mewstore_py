from flask import request, make_response, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from project.models import Good, db, User
from project.utils.Time_Transform import time_transform
from project.utils.log import logger


class Search(Resource):  # 搜索商品
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        keywords = request.args.get('keywords', type=str, default='')
        # 查询
        if keywords == '':
            sql_good = db.session.query(Good).filter_by(status=1).order_by(Good.id.desc())
        else:
            sql_good = Good.query.filter(
                Good.status == 1,  # 只显示status为1的商品
                or_(
                    Good.game.like(f"%{keywords}%"),
                    Good.title.like(f"%{keywords}%"),
                    Good.content.like(f"%{keywords}%")
                )).order_by(Good.id.desc())
        goods = sql_good.paginate(page=page, per_page=size).items
        good_list = []
        for good in goods:
            seller = db.session.query(User).get(good.seller_id)
            good_dict = {"id": str(good.id), "view": good.view, "content": good.content, "game": good.game,
                         "title": good.title, "picture_url": good.picture, "status": good.status,
                         'add_time': time_transform(good.add_time), "seller_id": str(good.seller_id),
                         'price': good.price, 'seller_nickname': seller.nickname,
                         'seller_profile_photo': seller.profile_photo}
            good_list.append(good_dict)
        if not good_list:
            return make_response(jsonify(code=404, message='找不到有关的商品'), 404)
        logger.debug('获取搜索商品成功')
        # 返回结果
        return make_response(jsonify(code=200, message='获取搜索商品成功', data=good_list), 200)
