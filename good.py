import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse
from data import db, Good, app, User
from user import jwt_required, JWT_SECRET_KEY

# 定义应用和API
good = Blueprint('good', __name__)
api = Api(good)


class Goods(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        id = parser.parse_args().get('id')
        with app.app_context():
            # 查询
            good = db.session.query(Good).get(id)
            # 判断是否存在
            if not good:
                return make_response(jsonify(code=404, message='商品不存在'), 404)
            # 获取商品信息
            else:
                good.view += 1
                db.session.commit()
                good_info = {'id': good.id, 'view': good.view, 'content': good.content, 'game': good.game,
                             'title': good.title,
                             'status': good.status, 'sell_id': good.sell_id}
                # 返回结果
                return make_response(jsonify(code=200, message='获取商品信息成功', data=good_info), 200)

    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('view', type=int)
        parser.add_argument('content', type=str)
        parser.add_argument('game', type=str)
        parser.add_argument('title', type=str)
        parser.add_argument('account', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('status', type=int)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                # 查询
                account = db.session.query(Good).get(args['account'])
                # 判断是否存在
                if account:
                    return make_response(jsonify(code=404, message='商品已存在'), 404)
                else:
                    # 创建商品
                    good = Good(view=args['view'], content=args['content'], game=args['game'], title=args['title'],
                                account=args['account'], password=args['password'], status=args['status'],
                                sell_id=user.id)
                    # 提交修改
                    db.session.add(good)
                    db.session.commit()
                    # 返回结果
                    return make_response(jsonify(code=200, message='创建商品信息成功'), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)

    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('view', type=int)
        parser.add_argument('content', type=str)
        parser.add_argument('game', type=str)
        parser.add_argument('title', type=str)
        parser.add_argument('account', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('status', type=int)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                user = user
                # 查询
                good = db.session.query(Good).get(args['id'])
                # 判断是否存在
                if not good:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                # 修改商品信息
                good.content = args['content']
                good.game = args['game']
                good.title = args['title']
                good.account = args['account']
                good.password = args['password']
                good.status = args['status']
                good.sell_id = user.id
                # 提交修改
                db.session.commit()
                # 返回结果
                return make_response(jsonify(code=200, message='修改商品信息成功'), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)

    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        id = parser.parse_args().get('id')
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user:
                # 查询
                good = db.session.query(Good).get(id)
                # 判断是否存在
                if not good:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                # 删除商品
                db.session.delete(good)
                # 提交修改
                db.session.commit()
                # 返回结果
                return make_response(jsonify(code=200, message='删除商品成功'), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


api.add_resource(Goods, '/good')
