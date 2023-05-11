from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash, generate_password_hash

from project.models import User, db
from project.utils.auth import jwt_required
from project.utils.log import logger


class User_password(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('old_password', type=str, required=True, help='请输入原密码')
        parser.add_argument('password', type=str, required=True, help='请输入新密码')
        parser.add_argument('check_password', type=str, required=True, help='请输入确认密码')
        args = parser.parse_args()
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            if check_password_hash(user.password, args['old_password']):
                if args['password'] == args['check_password']:
                    user.password = generate_password_hash(args['password'])
                    db.session.commit()
                    logger.debug('修改密码成功')
                    return make_response(jsonify(code=201, message='修改密码成功'), 201)
                else:
                    return make_response(jsonify(code=400, message='两次输入的密码不一致'), 400)
            else:
                return make_response(jsonify(code=401, message='原密码错误'), 401)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
