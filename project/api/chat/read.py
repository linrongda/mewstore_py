from flask import request, make_response, jsonify
from flask_restful import Resource, reqparse

from project.models import db, Messages
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class MessageRead(Resource):  # 用户已读消息
    @jwt_required
    @check_status([0, 3])
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('send_id', type=str, required=True, help='请输入发送者id')
        parser.add_argument('message_id', type=str, required=True, help='请输入信息id')
        args = parser.parse_args()
        send_id = args.get('send_id')
        message_id = args.get('message_id')
        message = db.session.query(Messages).filter_by(id=message_id, send_id=send_id, is_read=0).first()
        if message:
            message.is_read = 1
            db.session.commit()
            logger.debug(f'消息{message_id}已读')
            return make_response(jsonify(code=201, message='消息已读'), 201)
        else:
            return make_response(jsonify(code=404, message='消息不存在或已读'), 404)
