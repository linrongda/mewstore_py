from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from project.models import db
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger
from project.utils.upload import upload_photo


class User_profile_photo(Resource):  # 修改用户头像
    @jwt_required
    @check_status([0, 3])
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('profile_photo', type=FileStorage, location=['files'], required=True, help='请上传头像')
        args = parser.parse_args()
        user = request.user
        user.profile_photo = upload_photo(args['profile_photo'])
        db.session.commit()
        logger.debug(f'用户{user.username}修改头像成功')
        return make_response(jsonify(code=201, message='修改头像成功'), 201)
