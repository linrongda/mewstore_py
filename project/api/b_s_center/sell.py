from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import User, db, Good
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required
from project.utils.log import logger


class Sell(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            # 查询
            sql_goods = db.session.query(Good).filter_by(seller_id=user.id)
            goods = sql_goods.paginate(page=page, per_page=size).items
            good_list = []
            for good in goods:
                if not good.picture:
                    picture_url = None
                else:
                    picture_urls = good.picture.split(',')
                    picture_url = []
                    for picture in picture_urls:
                        picture = 'http://rtqcx0dtq.bkt.clouddn.com/' + picture
                        picture_url.append(picture)
                good_dict = {'id': good.id, 'view': good.view, 'game': good.game, 'title': good.title,
                             'content': good.content, 'picture_url': picture_url,
                             'add_time': time_transform(good.add_time),
                             'status': good.status, 'seller_id': good.seller_id, 'price': good.price}
                good_list.append(good_dict)
            logger.debug('获取出售商品成功')
            # 返回结果
            return make_response(jsonify(code=200, message='获取出售商品成功', data=good_list), 200)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
