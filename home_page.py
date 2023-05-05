import logging

from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource
from sqlalchemy import or_

from api.data import db, app, Good

# 定义应用和API
home_page = Blueprint('home_page', __name__)
api = Api(home_page)

logger = logging.getLogger(__name__)


class HomePage(Resource):
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        with app.app_context():
            # 查询
            sql_good = db.session.query(Good).filter_by(status=0).order_by(Good.id.desc())
            goods = sql_good.paginate(page=page, per_page=size).items
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
                good_dict = {"id": good.id, "view": good.view, "content": good.content, "game": good.game,
                             "title": good.title, "picture_url": picture_url, "status": good.status,
                             'add_time': good.add_time, "seller_id": good.seller_id, "price": good.price}
                good_list.append(good_dict)
            if not good_list:
                return make_response(jsonify(code=404, message='找不到在售的商品'), 404)
            logger.debug('获取商品成功')
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)


class Search(Resource):
    def get(self):
        page = request.args.get('page', type=int, default=1)
        size = request.args.get('size', type=int, default=4)
        keywords = request.args.get('keywords', type=str, default='')
        with app.app_context():
            # 查询
            if keywords == '':
                sql_good = db.session.query(Good).filter_by(status=0).order_by(Good.id.desc())
            else:
                sql_good = Good.query.filter(
                    Good.status == 0,  # 只显示status为0的商品
                    or_(
                        Good.game.like(f"%{keywords}%"),
                        Good.title.like(f"%{keywords}%"),
                        Good.content.like(f"%{keywords}%")
                    )).order_by(Good.id.desc())
            goods = sql_good.paginate(page=page, per_page=size).items
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
                good_dict = {"id": good.id, "view": good.view, "content": good.content, "game": good.game,
                             "title": good.title, "picture_url": picture_url, "status": good.status,
                             'add_time': good.add_time, "seller_id": good.seller_id}
                good_list.append(good_dict)
            if not good_list:
                return make_response(jsonify(code=404, message='找不到有关的商品'), 404)
            logger.debug('获取商品成功')
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品成功', data=good_list), 200)


api.add_resource(HomePage, '/home-page')
api.add_resource(Search, '/search')
