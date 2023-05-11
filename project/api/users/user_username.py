from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import User
from project.utils.auth import jwt_required
from project.utils.log import logger


class User_username(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        args = parser.parse_args()
        # with app.app_context():
        from project.exts import db
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            if db.session.query(User).filter(User.username == args['username']).first():
                return make_response(jsonify(code=400, message='该用户名已存在'), 400)
            user.username = args['username']
            db.session.commit()
            logger.debug('修改用户名成功')
            return make_response(jsonify(code=201, message='修改用户名成功'), 201)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
