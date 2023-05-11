from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from project.models import User, db
from project.utils.auth import jwt_required
from project.utils.log import logger
from project.utils.upload import upload_photo


class User_profile_photo(Resource):
    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('profile_photo', type=FileStorage, location=['files'], required=True, help='请上传头像')
        args = parser.parse_args()
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in (0, 3):
            # if user.profile_photo:
            #     delete_photo(user.profile_photo)
            user.profile_photo = upload_photo(args['profile_photo'])
            db.session.commit()
            logger.debug('修改头像成功')
            return make_response(jsonify(code=201, message='修改头像成功'), 201)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
