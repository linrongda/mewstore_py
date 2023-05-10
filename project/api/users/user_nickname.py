from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

# from project.app import app
from project.models import User, db
from project.utils.auth import jwt_required
from project.utils.log import logger


class User_nickname(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True, help='请输入昵称')
        args = parser.parse_args()
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            user.nickname = args['nickname']
            db.session.commit()
            logger.debug('修改昵称成功')
            return make_response(jsonify(code=201, message='修改昵称成功'), 201)
        else:
            return make_response(jsonify(code=403, message='error'), 403)
