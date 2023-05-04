import logging

import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse

from api.data import db, app, User, Favorite, Good
from api.user import jwt_required, JWT_SECRET_KEY

# 定义应用和API
b_s_center = Blueprint('b_s_center', __name__)
api = Api(b_s_center)

logger = logging.getLogger(__name__)


class Favorite_add(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('good_id', type=int, required=True, help='商品id必须提供')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
                # 查询
                favorite = db.session.query(Favorite).filter_by(user_id=user.id, good_id=args['good_id']).first()
                if favorite:
                    return make_response(jsonify(code=400, message='已收藏'), 400)
                good = db.session.query(Good).get(args['good_id'])
                if not good:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                else:
                    # 添加
                    favorite = Favorite(user_id=user.id, good_id=args['good_id'])
                    db.session.add(favorite)
                    good.view += 1
                    db.session.commit()
                    logger.debug('收藏成功')
                    # 返回结果
                    return make_response(jsonify(code=201, message='收藏成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


class Favorite_get(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
                # 查询
                sql_favorites = db.session.query(Favorite).filter_by(user_id=user.id)
                favorites = sql_favorites.paginate(page=page, per_page=size).items
                favorite_list = []
                for favorite in favorites:
                    good = db.session.query(Good).get(favorite.good_id)
                    favorite_dict = {'id': good.id, 'view': good.view, 'game': good.game,
                                     'title': good.title, 'content': good.content, 'picture_url': good.picture,
                                     'status': good.status, 'seller_id': good.seller_id, 'price': good.price,
                                     "good_id": favorite.good_id, "user_id": favorite.user_id}
                    favorite_list.append(favorite_dict)
                logger.debug('查询收藏的商品成功')
                # 返回结果
                return make_response(jsonify(code=200, message='查询收藏的商品成功', data=favorite_list), 200)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


class Sell(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status in (0, 3):
                # 查询
                sql_goods = db.session.query(Good).filter_by(seller_id=user.id)
                goods = sql_goods.paginate(page=page, per_page=size).items
                good_list = []
                for good in goods:
                    picture_urls = good.picture.split(',')
                    picture_url = []
                    for picture in picture_urls:
                        picture = 'http://rtqcx0dtq.bkt.clouddn.com/' + picture
                        picture_url.append(picture)
                    good_dict = {'id': good.id, 'view': good.view, 'game': good.game, 'title': good.title,
                                 'content': good.content, 'picture_url': picture_url, 'add_time': good.add_time,
                                 'status': good.status, 'seller_id': good.seller_id, 'price': good.price}
                    good_list.append(good_dict)
                logger.debug('获取出售商品成功')
                # 返回结果
                return make_response(jsonify(code=200, message='获取出售商品成功', data=good_list), 200)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


# class Purchased(Resource):
#     @jwt_required
#     def get(self):
#         page = request.args.get('page', type=int, default=1)
#         size = request.args.get('size', type=int, default=4)
#         token = request.headers.get('Authorization')
#         user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
#         with app.app_context():
#             user = db.session.query(User).get(user_id)
#             if user and user.status in (0, 3):
#                 # 查询
#                 sql_orders = db.session.query(Orders).filter_by(buyer_id=user.id, status=1)
#                 orders = sql_orders.paginate(page=page, per_page=size).items
#                 order_list = []
#                 for order in orders:
#                     order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
#                                   "seller_id": order.seller_id, "generate_time": order.generate_time,
#                                   "status": order.status, "price": order.price,
#                                   "buyer_status": order.buyer_status, "seller_status": order.seller_status}
#                     order_list.append(order_dict)
#                 logger.debug('获取已购买订单成功')
#                 # 返回结果
#                 return make_response(jsonify(code=200, message='获取已购买订单成功', data=order_list), 200)
#             else:
#                 return make_response(jsonify(code=403, message='你没有权限'), 403)
#
#
# class Bid(Resource):
#     @jwt_required
#     def get(self):
#         page = request.args.get('page', type=int, default=1)
#         size = request.args.get('size', type=int, default=4)
#         token = request.headers.get('Authorization')
#         user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
#         with app.app_context():
#             user = db.session.query(User).get(user_id)
#             if user and user.status in (0, 3):
#                 # 查询
#                 sql_orders = db.session.query(Orders).filter_by(buyer_id=user.id, status=0)
#                 orders = sql_orders.paginate(page=page, per_page=size).items
#                 order_list = []
#                 for order in orders:
#                     order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
#                                   "seller_id": order.seller_id, "generate_time": order.generate_time,
#                                   "status": order.status, "price": order.price,
#                                   "buyer_status": order.buyer_status, "seller_status": order.seller_status}
#                     order_list.append(order_dict)
#                 logger.debug('获取出价订单成功')
#                 # 返回结果
#                 return make_response(jsonify(code=200, message='获取出价订单成功', data=order_list), 200)
#             else:
#                 return make_response(jsonify(code=403, message='你没有权限'), 403)


# class Sold(Resource):
#     @jwt_required
#     def get(self):
#         page = request.args.get('page', type=int, default=1)
#         size = request.args.get('size', type=int, default=4)
#         token = request.headers.get('Authorization')
#         user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
#         with app.app_context():
#             user = db.session.query(User).get(user_id)
#             if user and user.status in (0, 3):
#                 # 查询
#                 sql_orders = db.session.query(Orders).filter_by(seller_id=user.id, status=1)
#                 orders = sql_orders.paginate(page=page, per_page=size).items
#                 order_list = []
#                 for order in orders:
#                     order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
#                                   "seller_id": order.seller_id, "generate_time": order.generate_time,
#                                   "status": order.status, "price": order.price,
#                                   "buyer_status": order.buyer_status, "seller_status": order.seller_status}
#                     order_list.append(order_dict)
#                 logger.debug('获取已完成订单成功')
#                 # 返回结果
#                 return make_response(jsonify(code=200, message='获取已完成订单成功', data=order_list), 200)
#             else:
#                 return make_response(jsonify(code=403, message='你没有权限'), 403)
#
#
# class Selling(Resource):
#     @jwt_required
#     def get(self):
#         page = request.args.get('page', type=int, default=1)
#         size = request.args.get('size', type=int, default=4)
#         token = request.headers.get('Authorization')
#         user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
#         with app.app_context():
#             user = db.session.query(User).get(user_id)
#             if user and user.status in (0, 3):
#                 # 查询
#                 sql_orders = db.session.query(Orders).filter_by(buyer_id=user.id, status=0)
#                 orders = sql_orders.paginate(page=page, per_page=size).items
#                 order_list = []
#                 for order in orders:
#                     order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
#                                   "seller_id": order.seller_id, "generate_time": order.generate_time,
#                                   "status": order.status, "price": order.price,
#                                   "buyer_status": order.buyer_status, "seller_status": order.seller_status}
#                     order_list.append(order_dict)
#                 logger.debug('获取正在交易订单成功')
#                 # 返回结果
#                 return make_response(jsonify(code=200, message='获取正在交易订单成功', data=order_list), 200)
#             else:
#                 return make_response(jsonify(code=403, message='你没有权限'), 403)


# api.add_resource(Purchased, '/users/purchased')
api.add_resource(Sell, '/users/goods')
api.add_resource(Favorite_add, '/users/favorites')
api.add_resource(Favorite_get, '/users/favorites')
# api.add_resource(Bid, '/users/bid')
# api.add_resource(Sold, '/users/sold')
# api.add_resource(Selling, '/users/selling')
