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
            Messages.send_time.desc()).all()
        send_list = Messages.query.filter_by(send_id=user_id).order_by(Messages.send_time.desc()).all()

        chat_lists = list(set(receive_list + send_list))
        chat_lists = sorted(chat_lists, key=lambda x: x.send_time)
        results = []
        conversation_partners = set()
        for conversation in chat_lists:
            other_person_id = (
                conversation.send_id
                if conversation.send_id != user_id
                else conversation.receive_id
            )
            if other_person_id not in conversation_partners:
                conversation_partners.add(other_person_id)
        for other_person_id in conversation_partners:
            person = db.session.query(User).get(other_person_id)
            receive_history = Messages.query.filter(
                Messages.send_id == other_person_id, Messages.receive_id == user_id).order_by(
                Messages.send_time.asc()).all()
            send_history = Messages.query.filter(
                Messages.send_id == user_id, Messages.receive_id == other_person_id).order_by(
                Messages.send_time.asc()).all()
            message_history = list(set(receive_history + send_history))
            message_history = sorted(message_history, key=lambda x: x.send_time)
            conversation = message_history[-1]
            results.append({'person_id': person.id, 'person_nickname': person.nickname,
                            'person_profie_photo': person.profile_photo, 'last_message_id': conversation.id,
                            'last_message': conversation.message,
                            'last_message_time': time_transform(conversation.send_time)})

        if not results:
            return make_response(jsonify({'code': 400, 'message': '暂无消息'}), 400)
        logger.debug(f'用户{user_id}获取历史消息')
        return make_response(jsonify({'code': 200, 'message': '获取成功', 'data': results}), 200)
