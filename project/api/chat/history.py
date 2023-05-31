from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import Messages
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class MessageHistory(Resource):  # 用户获取历史消息
    @jwt_required
    @check_status([0, 3])
    def get(self):
        receive_id = request.payload_id
        send_id = request.headers.get('send_id')
        # 查询数据库中的历史记录
        receive_history = Messages.query.filter(
            Messages.send_id == send_id, Messages.receive_id == receive_id, Messages.is_read == 1).order_by(
            Messages.send_time.asc()).all()

        send_history = Messages.query.filter(
            Messages.send_id == receive_id, Messages.receive_id == send_id, Messages.is_read == 1).order_by(
            Messages.send_time.asc()).all()

        message_history = list(set(receive_history + send_history))
        message_history = sorted(message_history, key=lambda x: x.send_time)
        message_list = []
        # 发送历史记录给接收者
        for message in message_history:
            message_dict = {'send_id': str(message.send_id), 'message': message.message, 'message_id': str(message.id),
                            'type': message.type, 'send_time': time_transform(message.send_time)}
            message_list.append(message_dict)
        if not message_list:
            return make_response(jsonify({'code': 400, 'message': '暂无历史消息'}), 400)
        logger.debug(f'用户{receive_id}获取与用户{send_id}的历史消息')
        return make_response(jsonify({'code': 200, 'message': '获取成功', 'data': message_list}), 200)
