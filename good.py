from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse
import data
from user import jwt_required

# 定义应用和API
good = Blueprint('good', __name__)
api = Api(good)


class Good(Resource):
    # 获取商品信息
    def __int__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int)
        self.parser.add_argument('view', type=int)
        self.parser.add_argument('content', type=str)
        self.parser.add_argument('game', type=str)
        self.parser.add_argument('title', type=str)
        self.parser.add_argument('account', type=str)
        self.parser.add_argument('password', type=str)
        self.parser.add_argument('status', type=int)
        self.parser.add_argument('sell_id', type=int)
        self.args = self.parser.parse_args()
        self.id = self.args.get('id')
        self.view = self.args.get('view')
        self.content = self.args.get('content')
        self.game = self.args.get('game')
        self.title = self.args.get('title')
        self.account = self.args.get('account')
        self.password = self.args.get('password')
        self.status = self.args.get('status')
        self.sell_id = self.args.get('sell_id')

    def get(self):
        # 查询
        self.good = data.session.query(data.Good).get(self.id)
        # 判断是否存在
        if not self.good:
            return make_response(jsonify(code=404, message='商品不存在'), 404)
        # 获取商品信息
        else:
            self.good.view += 1
            data.session.commit()
            good_info = {'id': self.good.id, 'view': self.good.view, 'content': self.good.content, 'game': self.good.game, 'title': self.good.title,
                         'status': self.good.status, 'sell_id': self.good.sell_id}
            # 返回结果
            return make_response(jsonify(code=200, message='获取商品信息成功', data=good_info), 200)

    @jwt_required(lambda payload: payload['status'] == '0')
    def post(self):
        user_id = request.jwt_payload['id']
        user = data.session.query(data.User).get(user_id)
        if user:
            self.user = user
            # 查询
            account = data.session.query(data.Good).get(self.account)
            # 判断是否存在
            if account:
                return make_response(jsonify(code=404, message='商品已存在'), 404)
            else:
                # 创建商品
                self.good = data.Good(view=self.view, content=self.content, game=self.game, title=self.title,
                                 account=self.account, password=self.password, status=self.status, sell_id=self.user.id)
                # 提交修改
                data.session.add(self.good)
                data.session.commit()
                # 返回结果
                return make_response(jsonify(code=200, message='创建商品信息成功'), 200)
        else:
            return make_response(jsonify(code=404, message='用户不存在'), 404)

    @jwt_required(lambda payload: request.jwt_payload['status'] == '0')
    def put(self):
        user_id = request.jwt_payload['id']
        user = data.session.query(data.User).get(user_id)
        if user:
            self.user = user
            # 查询
            self.good = data.session.query(data.Good).get(self.id)
            # 判断是否存在
            if not self.good:
                return make_response(jsonify(code=404, message='商品不存在'), 404)
            # 修改商品信息
            self.good.content = self.content
            self.good.game = self.game
            self.good.title = self.title
            self.good.account = self.account
            self.good.password = self.password
            self.good.status = self.status
            self.good.sell_id = self.sell_id
            # 提交修改
            data.session.commit()
            # 返回结果
            return make_response(jsonify(code=200, message='修改商品信息成功'), 200)
        else:
            return make_response(jsonify(code=404, message='用户不存在'), 404)

    @jwt_required(lambda payload: request.jwt_payload['status'] == '0')
    def delete(self):
        user_id = request.jwt_payload['id']
        user = data.session.query(data.User).get(user_id)
        if user:
            self.user = user
            # 查询
            self.good = data.session.query(data.Good).get(self.id)
            # 判断是否存在
            if not self.good:
                return make_response(jsonify(code=404, message='商品不存在'), 404)
            # 删除商品
            data.session.delete(good)
            # 提交修改
            data.session.commit()
            # 返回结果
            return make_response(jsonify(code=200, message='删除商品成功'), 200)
        else:
            return make_response(jsonify(code=404, message='用户不存在'), 404)


api.add_resource(Good, '/good')
