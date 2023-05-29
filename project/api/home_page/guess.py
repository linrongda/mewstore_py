from random import shuffle

from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import Good, db, Favorite, User
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Guess(Resource):
    @jwt_required
    @check_status([0, 3])
    def get(self):
        # with app.app_context():
        # 查询
        favorites = db.session.query(Favorite).filter_by(user_id=request.payload_id).all()
        fav_count = len(favorites)
        game_type = game_num = {'王者荣耀': 0, '英雄联盟': 0, '原神': 0, '绝地求生': 0, '和平精英': 0, '第五人格': 0}
        for favorite in favorites:
            good = db.session.query(Good).filter_by(id=favorite.good_id).first()
            if good and good.game in game_type:
                game_type[good.game] += 1
        fav_total = 0
        for game in game_type:
            game_rate = game_type[game] / fav_count
            game_num[game] = int(15 * game_rate)
            fav_total += game_num[game]
        remain = 20 - fav_total
        recommended_items = []
        for game, count in game_num.items():
            items = Good.query.filter_by(game=game, status=1).all()
            shuffle(items)
            items = items[:count]
            recommended_items.extend(items)
        remaining_items = Good.query.filter(~Good.id.in_([item.id for item in recommended_items]),
                                            Good.status == 1).all()
        shuffle(remaining_items)
        # Take the required number of remaining items
        remaining_items = remaining_items[:remain]
        # Combine the recommended and remaining items
        all_items = recommended_items + remaining_items
        # Shuffle the combined items
        shuffle(all_items)
        good_list = []
        for good in all_items:
            if not good.picture:
                picture_url = None
            else:
                picture_urls = good.picture.split(',')
                picture_url = []
                for picture in picture_urls:
                    picture = 'http://rtqcx0dtq.bkt.clouddn.com/' + picture
                    picture_url.append(picture)
            good_dict = {"id": good.id, "view": good.view, "content": good.content, "game": good.game,
                         "title": good.title, "picture_url": picture_url, "status": good.status,
                         'add_time': time_transform(good.add_time), "seller_id": good.seller_id,
                         "price": good.price}
            good_list.append(good_dict)
        if not good_list:
            return make_response(jsonify(code=404, message='找不到在售的商品'), 404)
        logger.debug('获取商品成功')
        # 返回结果
        return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)
