from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage

from project.utils.auth import jwt_required, check_status
from project.utils.log import logger

from project.utils.upload import upload_photo


class Picture(Resource):
    @jwt_required
    @check_status([0, 3])
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('picture', type=FileStorage, location=['files'], action=['append'],
                            help='请上传有效格式的图片', required=True)
        args = parser.parse_args()
        # with app.app_context():
        if isinstance(args['picture'], list):
            picture_list = []
            for picture in args['picture']:
                picture = 'http://rtqcx0dtq.bkt.clouddn.com/' + upload_photo(picture)
                picture_list.append(picture)
            pictures = ','.join(picture_list)
        else:
            pictures = 'http://rtqcx0dtq.bkt.clouddn.com/' + upload_photo(args['picture'])
        logger.debug('上传图片成功')
        return make_response(jsonify(code=201, message='上传图片成功', data=pictures), 201)
