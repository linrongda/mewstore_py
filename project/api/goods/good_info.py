from flask import make_response, jsonify
from flask_restful import Resource

from project.models import Good, db
from project.utils.Time_Transform import time_transform
from project.utils.log import logger


class Good_get(Resource):  # 获取商品信息
    def get(self, good_id):
        # 查询
        good = db.session.query(Good).get(good_id)
        # 判断是否存在
        if not good:
            return make_response(jsonify(code=404, message='商品不存在'), 404)
        # 获取商品信息
        else:
            if not good.picture:
                picture_url = None
            else:
                picture_urls = good.picture.split(',')
                picture_url = []
                for picture in picture_urls:
                    picture = 'http://rtqcx0dtq.bkt.clouddn.com/' + picture
                    picture_url.append(picture)
            good_info = {'id': good.id, 'view': good.view, 'game': good.game, 'picture_url': picture_url,
                         'title': good.title, 'content': good.content, 'add_time': time_transform(good.add_time),
                         'status': good.status, 'seller_id': good.seller_id, 'price': good.price}
            logger.debug(f'获取商品{good.id}信息成功')
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品信息成功', data=good_info), 200)
