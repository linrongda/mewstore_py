import logging
import datetime

from flask import request, jsonify, Blueprint, make_response
from flask_restful import Api, Resource, reqparse
from werkzeug.datastructures import FileStorage

from api.data import db, Good, app, User
from api.snowflake import id_generate
from api.user import jwt_required, upload_photo

# 定义应用和API
good = Blueprint('good', __name__)
api = Api(good)

logger = logging.getLogger(__name__)

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


def time_transform(timestamp):
    local_time = timestamp + datetime.timedelta(hours=8)  # 加上8小时是因为中国位于UTC+8时区
    local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
    return local_time_str


class Good_get(Resource):
    def get(self, good_id):
        with app.app_context():
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
                logger.debug('获取商品信息成功')
                # 返回结果
                return make_response(jsonify(code=200, message='获取商品信息成功', data=good_info), 200)


class Good_add(Resource):
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('game', type=str, required=True, location=['form'], help='游戏名不能为空')
        parser.add_argument('title', type=str, required=True, location=['form'], help='标题不能为空')
        parser.add_argument('content', type=str, required=True, location=['form'], help='内容不能为空')
        parser.add_argument('picture', type=FileStorage, location=['files'], action=['append'],
                            help='请上传有效格式的图片')
        parser.add_argument('account', type=str, required=True, location=['form'], help='账号不能为空')
        parser.add_argument('password', type=str, required=True, location=['form'], help='密码不能为空')
        parser.add_argument('price', type=float, required=True, location=['form'], help='价格不能为空')
        args = parser.parse_args()
        with app.app_context():
            user = db.session.query(User).get(request.payload_id)
            if user and user.status in (0, 3):
                # 查询
                is_good = db.session.query(Good).filter_by(account=args['account'], game=args['game']).first()
                # 判断是否存在
                if is_good:
                    return make_response(jsonify(code=400, message='商品已存在'), 400)
                else:
                    # 使用 CBC 模式对密码进行加密
                    encrypted_password = encrypt_aes_cbc(args['password'])
                    # 创建商品
                    if args['picture']:
                        if isinstance(args['picture'], list):
                            picture_list = []
                            for picture in args['picture']:
                                picture = upload_photo(picture)
                                picture_list.append(picture)
                            pictures = ','.join(picture_list)
                        else:
                            pictures = upload_photo(args['picture'])
                    good = Good(id=id_generate('good'), view=0, game=args['game'],
                                title=args['title'], content=args['content'], picture=pictures,
                                account=args['account'], password=encrypted_password, status=0,
                                seller_id=user.id, price=args['price'], add_time=datetime.datetime.utcnow())
                    # 提交修改
                    db.session.add(good)
                    db.session.commit()
                    logger.debug('创建商品信息成功')
                    # 返回结果
                    # # 使用 CBC 模式对密码进行解密
                    # decrypted_password = decrypt_aes_cbc(encrypted_password)
                    return make_response(jsonify(code=201, message='创建商品信息成功'), 201)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


class Good_update(Resource):
    @jwt_required
    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, location=['form'], help='商品id不能为空')
        parser.add_argument('game', type=str, location=['form'])
        parser.add_argument('title', type=str, location=['form'])
        parser.add_argument('content', type=str, location=['form'])
        parser.add_argument('picture', type=FileStorage, action=['append'], location=['files'],
                            help='请上传有效格式的图片')
        parser.add_argument('account', type=str, location=['form'])
        parser.add_argument('password', type=str, location=['form'])
        parser.add_argument('status', type=int, location=['form'])
        parser.add_argument('price', type=float, location=['form'])
        args = parser.parse_args()
        with app.app_context():
            user = db.session.query(User).get(request.payload_id)
            if user and user.status in (0, 3):
                # 查询
                good = db.session.query(Good).get(args['id'])
                # 判断是否存在
                if not good or good.seller_id != user.id:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                # 修改商品信息
                if args['game']:
                    good.game = args['game']
                if args['content']:
                    good.content = args['content']
                if args['title']:
                    good.title = args['title']
                if args['picture']:  # 此处不能删除照片，防止有人的头像或商品图是这里的商品图（有可能），从而把头像删了
                    if isinstance(args['picture'], list):
                        picture_list = []
                        for picture in args['picture']:
                            picture = upload_photo(picture)
                            picture_list.append(picture)
                        pictures = ','.join(picture_list)
                        good.picture = pictures
                    else:
                        picture = upload_photo(args['picture'])
                        good.picture = picture
                if args['account']:
                    good.account = args['account']
                if args['password']:
                    good.password = encrypt_aes_cbc(args['password'])
                if args['status']:
                    good.status = args['status']
                if args['price']:
                    good.price = args['price']
                # 提交修改
                db.session.commit()
                logger.debug('修改商品信息成功')
                # 返回结果
                return make_response(jsonify(code=201, message='修改商品信息成功'), 201)
            else:
                return make_response(jsonify(code=403, message='用户不存在'), 403)


class Good_delete(Resource):
    @jwt_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True, help='商品id不能为空')
        id = parser.parse_args().get('id')
        with app.app_context():
            user = db.session.query(User).get(request.payload_id)
            if user and user.status in (0, 3):
                # 查询
                good = db.session.query(Good).get(id)
                # 判断是否存在
                if not good or good.seller_id != user.id:
                    return make_response(jsonify(code=404, message='商品不存在'), 404)
                # 删除商品
                db.session.delete(good)
                # 提交修改
                db.session.commit()
                logger.debug('删除商品成功')
                # 返回结果
                return make_response(jsonify(code=204, message='删除商品成功'), 204)
            else:
                return make_response(jsonify(code=403, message='你没有权限'), 403)


api.add_resource(Good_get, '/goods/<int:good_id>')
api.add_resource(Good_add, '/goods')
api.add_resource(Good_update, '/goods')
api.add_resource(Good_delete, '/goods')
