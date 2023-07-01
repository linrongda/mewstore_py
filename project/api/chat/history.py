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
        send_id = request.args.get('send_id', type=str)
        # 查询数据库中的历史记录
        receive_history = Messages.query.filter(
            Messages.send_id == send_id, Messages.receive_id == receive_id, Messages.is_read == 1).order_by(
            Messages.send_time.asc()).all()  # 查询用户作为接收者且已读的消息，且不是系统消息
        send_history = Messages.query.filter(
            Messages.send_id == receive_id, Messages.receive_id == send_id, Messages.is_read == 1).order_by(
            Messages.send_time.asc()).all()  # 查询用户作为发送者且已读的消息
        message_history = list(set(receive_history + send_history))  # 去重
        message_history = sorted(message_history, key=lambda x: x.send_time)  # 按照时间排序
        message_list = []
        # 添加消息到列表中
        for message in message_history:
            message_dict = {'send_id': str(message.send_id), 'receive_id': str(message.receive_id),
                            'message': message.message, 'message_id': str(message.id),
                            'type': message.type, 'send_time': time_transform(message.send_time, True)}
            message_list.append(message_dict)
        if not message_list:
            return make_response(jsonify({'code': 404, 'message': '暂无历史消息'}), 404)
        logger.debug(f'用户{receive_id}获取与用户{send_id}的历史消息')
        return make_response(jsonify({'code': 200, 'message': '获取成功', 'data': message_list}), 200)
