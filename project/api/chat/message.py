import datetime
import json

import jwt
from flask import request
from flask_socketio import join_room, emit, Namespace

from project.models import db, User, Messages
from project.utils.Time_Transform import time_transform
from project.utils.auth import JWT_SECRET_KEY
from project.utils.snowflake import id_generate


class Message(Namespace):
    def on_connect(self):
        token = request.headers.get('Authorization')
        if user_id := self.verify_token(token):
            join_room(user_id)  # 将用户添加到以其唯一标识符命名的房间
            emit('response', {'code': 1, 'message': '连接成功'})
            self.send_offline_messages(user_id)
        else:
            emit('response', {'code': 0, 'message': '你没有权限'})

    # def on_join(self):
    #     token = request.headers.get('Authorization')
    #     if self.verify_token(token):
    #         data = request.get_json()  # 获取请求中的数据
    #         receive_id = data['receive_id']  # 获取消息的接收者的唯一标识符
    #         join_room(receive_id)  # 将用户添加到以其唯一标识符命名的房间
    #         emit('response', {'code': 2, 'message': '加入成功'})  # 发送消息给连接的用户
    #     else:
    #         emit('response', {'code': 0, 'message': '你没有权限'})

    def on_message(self, messages):
        token = request.headers.get('Authorization')
        if sender_id := self.verify_token(token):
            messages_dict = json.loads(messages)
            receive_id = messages_dict.get('receive_id')  # 获取消息的接收者的唯一标识符
            message_type = messages_dict.get('type')  # 获取消息类型
            message = messages_dict.get('message')  # 获取消息内容
            messages = Messages(id=id_generate('message'), isSystem=0, send_id=sender_id, receive_id=receive_id,
                                message=message, send_time=datetime.datetime.utcnow(), type=message_type, is_read=0)
            db.session.add(messages)
            db.session.flush()
            db.session.commit()
            emit('response', {'code': 200, 'message': message, 'message_id': str(messages.id), 'type': message_type},
                 room=receive_id)  # 发送消息给接收者的房间

            emit('response', {'code': 200, 'message': message, 'message_id': str(messages.id), 'type': message_type},
                 room=sender_id)  # 发送消息给发送者的房间
        else:
            emit('response', {'code': 400, 'message': '你没有权限'})

    # def on_leave(self):
    #     token = request.headers.get('Authorization')
    #     if self.verify_token(token):
    #         user_id = self.verify_token(token)  # 获取用户的唯一标识符
    #         leave_room(user_id)  # 将用户从房间中移除
    #         emit('response', {'code': 3, 'message': '退出成功'})  # 发送消息给断开连接的用户
    #     else:
    #         emit('response', {'code': 400, 'message': '你没有权限'})

    def verify_token(self, token):
        try:
            payload_id = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])['id']
            user = db.session.query(User).get(payload_id)
            if user and user.status in (0, 3):
                return user.id
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def send_offline_messages(self, receive_id):
        # 查询数据库中针对接收者的未读消息
        offline_messages = Messages.query.filter_by(receive_id=receive_id, is_read=0).filter(
            Messages.send_id != 6).all()

        # 将未读消息发送给接收者
        for message in offline_messages:
            emit('response',
                 {'code': 200, 'message': message.message, 'send_id': str(message.send_id), 'type': message.type,
                  'message_id': str(message.id), 'send_time': time_transform(message.send_time)},
                 room=receive_id)
