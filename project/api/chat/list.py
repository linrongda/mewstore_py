import datetime

from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import Messages, db, User
from project.utils.Time_Transform import time_transform
from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class Chat_list(Resource):  # 用户获取聊天列表
    @jwt_required
    @check_status([0, 3])
    def get(self):
        user_id = request.payload_id
        # 查询数据库中的历史记录
        receive_list = Messages.query.filter(Messages.receive_id == user_id, Messages.send_id != 6).order_by(
            Messages.send_time.asc()).all()  # 查询用户作为接收者的消息，且不是系统消息
        send_list = Messages.query.filter_by(send_id=user_id).order_by(Messages.send_time.asc()).all()  # 查询用户作为发送者的消息
        chat_lists = list(set(receive_list + send_list))  # 去重
        chat_lists = sorted(chat_lists, key=lambda x: x.send_time)  # 按照时间排序
        results = []
        # 获取系统消息
        system_list = Messages.query.filter(Messages.send_id == 6, Messages.receive_id == user_id).order_by(
            Messages.send_time.asc()).all()
        if system_list:
            conversation = system_list[-1]
            results.append({'person_id': str(6), 'person_nickname': '系统消息',
                            'person_profile_photo': 'http://qiniuyun.mewtopia.cn/FrXOPwQ9y5GrCPiU3lRjw7j3q5iu',
                            'last_message_id': str(conversation.id), 'last_message': conversation.message,
                            'last_message_time': time_transform(conversation.send_time - datetime.timedelta(hours=8),
                                                                True)})
        # 获取聊天列表
        conversation_partners = set()
        for conversation in chat_lists:  # 遍历所有的聊天记录
            other_person_id = (
                conversation.send_id
                if conversation.send_id != user_id
                else conversation.receive_id
            )  # 获取对方的id
            if other_person_id not in conversation_partners:  # 如果对方的id不在对话列表中
                conversation_partners.add(other_person_id)  # 将对方的id加入对话列表
        for other_person_id in conversation_partners:  # 遍历对话列表
            person = db.session.query(User).get(other_person_id)  # 获取对方的信息
            # 接下来同获取历史记录代码
            receive_history = Messages.query.filter(
                Messages.send_id == other_person_id, Messages.receive_id == user_id).order_by(
                Messages.send_time.asc()).all()
            send_history = Messages.query.filter(
                Messages.send_id == user_id, Messages.receive_id == other_person_id).order_by(
                Messages.send_time.asc()).all()
            message_history = list(set(receive_history + send_history))
            message_history = sorted(message_history, key=lambda x: x.send_time)
            conversation = message_history[-1]  # 获取最后一条消息
            results.append({'person_id': str(person.id), 'person_nickname': person.nickname,
                            'person_profile_photo': person.profile_photo, 'last_message_id': str(conversation.id),
                            'last_message': conversation.message,
                            'last_message_time': time_transform(conversation.send_time, True)})
        if not results:
            return make_response(jsonify({'code': 404, 'message': '暂无消息'}), 404)
        logger.debug(f'用户{user_id}获取消息列表')
        return make_response(jsonify({'code': 200, 'message': '获取消息列表成功', 'data': results}), 200)
