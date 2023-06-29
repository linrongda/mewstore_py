from flask import make_response, jsonify, request
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from project.utils.auth import jwt_required, check_status
from project.utils.log import logger
from project.utils.upload import upload_photo


class Picture(Resource):  # 上传图片
    @jwt_required
    @check_status([0, 3])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('picture', type=FileStorage, location=['files'], help='请上传有效格式的图片', required=True)
        args = parser.parse_args()
        picture = upload_photo(args['picture'])
        logger.debug(f'用户{request.user.username}上传图片{picture}成功')
        return make_response(jsonify(code=201, message='上传图片成功', data=picture), 201)
