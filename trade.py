import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse

from data import db, Order, app, User
from user import jwt_required, JWT_SECRET_KEY

# 定义应用和API
trade = Blueprint('trade', __name__)
api = Api(trade)


class Buyer(Resource):
    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                orders = db.session.query(Order).filter(Order.buyer_id == user.id).all()
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "status": order.status, "money": order.money,
                                  "buyer_status": order.buyer_status, "seller_status": order.seller_status}
                    order_list.append(order_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取订单成功', data=order_dict), 200)


class Shoper(Resource):
    @jwt_required
    def get(self):
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                orders = db.session.query(Order).filter(Order.seller_id == user.id).all()
                order_list = []
                for order in orders:
                    order_dict = {"id": order.id, "good_id": order.good_id, "buyer_id": order.buyer_id,
                                  "seller_id": order.seller_id, "status": order.status, "money": order.money,
                                  "buyer_status": order.buyer_status, "seller_status": order.seller_status}
                    order_list.append(order_dict)
                # 返回结果
                return make_response(jsonify(code=200, message='获取订单成功', data=order_dict), 200)


api.add_resource(Buyer, '/buyer')
api.add_resource(Shoper, '/shoper')
