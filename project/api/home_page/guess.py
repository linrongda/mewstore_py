from random import shuffle

from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import Good, db, Favorite
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Guess(Resource):  # 猜你喜欢
    @jwt_required
    @check_status([0, 3])
    def get(self):
        # 查询
        favorites = db.session.query(Favorite).filter_by(user_id=request.payload_id).all()
        fav_count = len(favorites)
        game_type = game_num = {'王者荣耀': 0, '英雄联盟': 0, '原神': 0, '绝地求生': 0, '和平精英': 0, '第五人格': 0}
        for favorite in favorites:  # 统计用户喜欢的游戏
            good = db.session.query(Good).filter_by(id=favorite.good_id).first()
            if good and good.game in game_type:
                game_type[good.game] += 1
        fav_total = 0
        for game in game_type:
            game_rate = game_type[game] / fav_count  # 计算用户喜欢的游戏的比例
            game_num[game] = int(15 * game_rate)  # 计算推荐中用户喜欢的游戏的数量
            fav_total += game_num[game]  # 计算推荐中用户喜欢的游戏的总数
        remain = 20 - fav_total  # 计算推荐中剩余商品数量
        recommended_items = []
        for game, count in game_num.items():
            items = Good.query.filter_by(game=game, status=1).all()  # 查询用户喜欢的游戏的商品
            shuffle(items)  # 打乱顺序
            items = items[:count]  # 根据数量取出用户喜欢的游戏的商品
            recommended_items.extend(items)
        remaining_items = Good.query.filter(~Good.id.in_([item.id for item in recommended_items]),
                                            Good.status == 1).all()  # 查询剩余商品
        shuffle(remaining_items)
        remaining_items = remaining_items[:remain]
        all_items = recommended_items + remaining_items  # 合并推荐的商品
        shuffle(all_items)  # 打乱所有推荐的商品顺序
        good_list = []
        for good in all_items:
            good_dict = {"id": good.id, "view": good.view, "content": good.content, "game": good.game,
                         "title": good.title, "picture_url": good.picture, "status": good.status,
                         'add_time': time_transform(good.add_time), "seller_id": good.seller_id,
                         "price": good.price}
            good_list.append(good_dict)
        if not good_list:
            return make_response(jsonify(code=404, message='找不到在售的商品'), 404)
        logger.debug(f'用户{request.user.username}获取猜你喜欢商品成功')
        # 返回结果
        return make_response(jsonify(code=200, message='获取猜你喜欢商品成功', data=good_list), 200)
