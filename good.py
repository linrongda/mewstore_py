import jwt
from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse

from data import db, Good, app, User
from user import jwt_required, JWT_SECRET_KEY
from snowflake import Snowflake

# 定义应用和API
good = Blueprint('good', __name__)
api = Api(good)

# 定义雪花算法实例
worker = Snowflake(1, 1)
# 设置AES加密
from Crypto.Cipher import AES
import base64

# 加密密钥
key = b'mewstoremewstore'
# 初始化向量
iv = b'mewstoremewstore'


# 使用 CBC 模式进行加密
def encrypt_aes_cbc(data):
    # 将加密内容填充到16的倍数
    length = 16 - (len(data) % 16)
    data += chr(length) * length
    # 创建加密器
    aes = AES.new(key, AES.MODE_CBC, iv)
    # 加密数据
    encrypted_data = aes.encrypt(data.encode('utf-8'))
    # 将加密结果进行 base64 编码
    return base64.b64encode(encrypted_data).decode('utf-8')


# 使用 CBC 模式进行解密
def decrypt_aes_cbc(encrypted_data):
    # 将加密结果进行 base64 解码
    encrypted_data = base64.b64decode(encrypted_data)
    # 创建解密器
    aes = AES.new(key, AES.MODE_CBC, iv)
    # 解密数据
    decrypted_data = aes.decrypt(encrypted_data)
    # 将解密结果进行去填充操作
    return decrypted_data[:-decrypted_data[-1]].decode('utf-8')


class Goods(Resource):

    def get(self, id):
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
        parser.add_argument('picture', type=str, location='files')
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                is_good = db.session.query(Good).filter_by(account=args['account'], game=args['game']).first()
                # 判断是否存在
                if is_good:
                    return make_response(jsonify(code=404, message='商品已存在'), 404)
                else:
                    # 使用 CBC 模式对密码进行加密
                    encrypted_password = encrypt_aes_cbc(args['password'])
                    # 创建商品
                    good = Good(id=worker.generate(1, 1), view=args['view'], content=args['content'], game=args['game'],
                                title=args['title'],
                                account=args['account'], password=encrypted_password, status=args['status'],
                                sell_id=user.id)
                    # 提交修改
                    db.session.add(good)
                    db.session.commit()
                    # 返回结果
                    # # 使用 CBC 模式对密码进行解密
                    # decrypted_password = decrypt_aes_cbc(encrypted_password)
                    return make_response(jsonify(code=200, message='创建商品信息成功'), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)

    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        parser.add_argument('content', type=str)
        parser.add_argument('title', type=str)
        parser.add_argument('account', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('status', type=int)
        args = parser.parse_args()
        token = request.headers.get('Authorization')
        user_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
        with app.app_context():
            user = db.session.query(User).get(user_id)
            if user and user.status == 0:
                # 查询
                good = db.session.query(Good).get(args['id'])
                # 判断是否存在
                if not good or good.sell_id != user.id:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                # 修改商品信息
                if args['content']:
                    good.content = args['content']
                if args['title']:
                    good.title = args['title']
                if args['account']:
                    good.account = args['account']
                if args['password']:
                    good.password = encrypt_aes_cbc(args['password'])
                if args['status']:
                    good.status = args['status']
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
            if user and user.status == 0:
                # 查询
                good = db.session.query(Good).get(id)
                # 判断是否存在
                if not good or good.sell_id != user.id:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                # 删除商品
                db.session.delete(good)
                # 提交修改
                db.session.commit()
                # 返回结果
                return make_response(jsonify(code=200, message='删除商品成功'), 200)
            else:
                return make_response(jsonify(code=404, message='用户不存在'), 404)


api.add_resource(Goods, '/good', '/good/<int:id>')
