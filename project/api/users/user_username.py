from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import User, db
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class User_username(Resource):  # 修改用户名
    @jwt_required
    @check_status([0, 3])
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        args = parser.parse_args()
        user = request.user
        if db.session.query(User).filter(User.username == args['username']).first():
            return make_response(jsonify(code=400, message='该用户名已存在'), 400)
        user.username = args['username']
        db.session.commit()
        logger.debug(f'用户{user.username}修改用户名成功')
        return make_response(jsonify(code=201, message='修改用户名成功'), 201)
