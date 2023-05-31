from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import db
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class User_nickname(Resource):  # 修改用户昵称
    @jwt_required
    @check_status([0, 3])
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True, help='请输入昵称')
        args = parser.parse_args()
        user = request.user
        user.nickname = args['nickname']
        db.session.commit()
        logger.debug(f'用户{user.username}修改昵称成功')
        return make_response(jsonify(code=201, message='修改昵称成功'), 201)
