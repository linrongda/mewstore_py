import datetime

from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from project.models import db, Good
from project.utils.aes import encrypt
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger
from project.utils.snowflake import id_generate
from project.utils.upload import upload_photo


class Good_add(Resource):  # 添加商品
    @jwt_required
    @check_status([0, 3])
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
        user = request.user
        # 查询
        is_good = db.session.query(Good).filter_by(account=args['account'], game=args['game']).first()
        # 判断是否存在
        if is_good:
            return make_response(jsonify(code=400, message='商品已存在'), 400)
        else:
            # 使用 CBC 模式对密码进行加密
            encrypted_password = encrypt(args['password'])
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
            else:
                pictures = None
            good = Good(id=id_generate('good'), view=0, game=args['game'],
                        title=args['title'], content=args['content'], picture=pictures,
                        account=args['account'], password=encrypted_password, status=0,
                        seller_id=user.id, price=args['price'], add_time=datetime.datetime.utcnow())
            # 提交修改
            db.session.add(good)
            db.session.flush()
            db.session.commit()
            logger.debug(f'用户{user.username}创建商品{args["title"]}信息成功')
            # 返回结果
            return make_response(jsonify(code=201, message='创建商品信息成功', data={'id': good.id}), 201)
