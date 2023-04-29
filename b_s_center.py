import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse

from data import db, Order, app, User, Favorite, Good
from user import jwt_required, JWT_SECRET_KEY

# 定义应用和API
b_s_center = Blueprint('b_s_center', __name__)
api = Api(b_s_center)


class Favorite_add(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('good_id', type=int)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                favorite = db.session.query(Favorite).filter_by(user_id=user.id, good_id=args['good_id']).first()
                if favorite:
                    return make_response(jsonify(code=200, message='已收藏'), 200)
                else:
                    # 添加
                    favorite = Favorite(user_id=user.id, good_id=args['good_id'])
                    db.session.add(favorite)
                    db.session.commit()
                    # 返回结果
                    return make_response(jsonify(code=200, message='收藏成功'), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


class Favorite_get(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                sql_favorites = db.session.query(Favorite).filter_by(user_id=user.id)
                favorites = sql_favorites.paginate(page=page, per_page=size).items
                favorite_list = []  # 这里需要前端通过id查询具体信息，可能需要修改
                for favorite in favorites:
                    favorite_dict = {"good_id": favorite.good_id, "user_id": favorite.user_id}
                    favorite_list.append(favorite_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='查询成功', data=favorite_list), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


class Bought(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                sql_orders = db.session.query(Order).filter_by(buyer_id=user.id, status=1)
                orders = sql_orders.paginate(page=page, per_page=size).items
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "status": order.status, "price": order.price,
                                  "buyer_status": order.buyer_status, "seller_status": order.seller_status}
                    order_list.append(order_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取订单成功', data=order_list), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


class Offered(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                sql_orders = db.session.query(Order).filter_by(buyer_id=user.id, status=0)
                orders = sql_orders.paginate(page=page, per_page=size).items
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "status": order.status, "price": order.price,
                                  "buyer_status": order.buyer_status, "seller_status": order.seller_status}
                    order_list.append(order_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取订单成功', data=order_list), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


class Sell(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                sql_goods = db.session.query(Good).filter_by(seller_id=user.id)
                goods = sql_goods.paginate().items
                good_list = []
                for good in goods:
                    picture_urls = good.picture.split(',')
                    picture_url = []
                    for picture in picture_urls:
                        picture = 'http://rtqcx0dtq.bkt.clouddn.com/' + picture
                        picture_url.append(picture)
                    good_dict = {'id': good.id, 'view': good.view, 'game': good.game,
                                 'title': good.title, 'content': good.content, 'picture_url': picture_url,
                                 'status': good.status, 'seller_id': good.seller_id, 'price': good.price}
                    good_list.append(good_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


class Sold(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                sql_orders = db.session.query(Order).filter_by(seller_id=user.id, status=1)
                orders = sql_orders.paginate(page=page, per_page=size).items
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "status": order.status, "price": order.price,
                                  "buyer_status": order.buyer_status, "seller_status": order.seller_status}
                    order_list.append(order_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取订单成功', data=order_list), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


class Selling(Resource):
    @jwt_required
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                sql_orders = db.session.query(Order).filter_by(buyer_id=user.id, status=0)
                orders = sql_orders.paginate(page=page, per_page=size).items
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "status": order.status, "price": order.price,
                                  "buyer_status": order.buyer_status, "seller_status": order.seller_status}
                    order_list.append(order_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取订单成功', data=order_list), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


api.add_resource(Bought, '/bought')
api.add_resource(Sell, '/sell')
api.add_resource(Favorite_add, '/user/favorite/add')
api.add_resource(Favorite_get, '/user/favorite')
api.add_resource(Offered, '/offered')
api.add_resource(Sold, '/sold')
api.add_resource(Selling, '/selling')
