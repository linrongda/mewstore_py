import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse

from data import db, Order, app, User, Good
from user import jwt_required, JWT_SECRET_KEY

# 定义应用和API
home_page = Blueprint('home_page', __name__)
api = Api(home_page)


class HomePage(Resource):
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        with app.app_context():
            # 查询
            sql_good = db.session.query(Good).Oder_by(Good.id.desc())
            goods = sql_good.paginate(page=page, per_page=size).items
            good_list = []
            for good in goods:
                good_dict = {"id": good.id, "view": good.view, "content": good.content, "game": good.game,
                             "title": good.title, "picture": good.picture, "status": good.status,
                             "seller_id": good.seller_id, "price": good.price}
                good_list.append(good_dict)
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)


class Search(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('text', type=str)
        args = parser.parse_args()
        text = args['text']
        with app.app_context():
            # 查询
            goods = db.session.query(Good).filter_by().all()
            good_list = []
            for good in goods:
                good_dict = {"id": good.id, "view": good.view, "content": good.content, "game": good.game,
                             "title": good.title, "picture": good.picture, "status": good.status,
                             "seller_id": good.seller_id}
                good_list.append(good_dict)
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)


api.add_resource(HomePage, '/home_page')
api.add_resource(Search, '/search')
