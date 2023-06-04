from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import db, Favorite, Good, User
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Favorite_get(Resource):  # 用户查询收藏
    @jwt_required
    @check_status([0, 3])
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        user = request.user
        # 查询
        sql_favorites = db.session.query(Favorite).filter_by(user_id=user.id)
        favorites = sql_favorites.paginate(page=page, per_page=size).items
        favorite_list = []
        for favorite in favorites:
            good = db.session.query(Good).get(favorite.good_id)
            seller = db.session.query(User).get(good.seller_id)
            favorite_dict = {'id': good.id, 'view': good.view, 'add_time': time_transform(good.add_time),
                             'game': good.game, 'title': good.title, 'content': good.content,
                             'picture_url': good.picture, 'status': good.status, 'seller_id': good.seller_id,
                             'price': good.price, "user_id": favorite.user_id, 'seller_nickname': seller.nickname,
                             'seller_profile_photo': seller.profile_photo}
            favorite_list.append(favorite_dict)
        logger.debug(f'用户{user.username}查询收藏的商品成功')
        # 返回结果
        return make_response(jsonify(code=200, message='查询收藏的商品成功', data=favorite_list), 200)
