import datetime

import jwt
from flask import request

from project.models import db, User, Messages

from flask_socketio import join_room, leave_room, emit, Namespace
from project.utils.auth import JWT_SECRET_KEY


class Message(Namespace):
    def on_connect(self):
        token = request.headers.get('Authorization')
        if self.verify_token(token):
            emit('response', {'code': 200, 'message': '连接成功'})
        else:
            emit('response', {'code': 400, 'message': '你没有权限'})

    def on_join(self):
        token = request.headers.get('Authorization')
        if self.verify_token(token):
            join_room(self.verify_token(token))  # 将用户添加到以其唯一标识符命名的房间
            emit('response', {'code': 200, 'message': '加入成功'})  # 发送消息给连接的用户
        else:
            emit('response', {'code': 400, 'message': '你没有权限'})

    def on_message(self):
        token = request.headers.get('Authorization')
        if self.verify_token(token):
            sender_id = self.verify_token(token)  # 获取发送消息的用户的唯一标识符
            data = request.get_json()  # 获取请求中的数据
            receive_id = data['receive_id']  # 获取消息的接收者的唯一标识符
            message = data['message']  # 获取消息内容
            message_type = data['type']  # 获取消息类型
            emit('message', message, room=receive_id)  # 发送消息给接收者的房间
            messages = Messages(send_id=sender_id, receive_id=receive_id, message=message,
                                send_time=datetime.datetime.utcnow(), type=message_type)
            db.session.add(messages)
            db.session.commit()
        else:
            emit('response', {'code': 400, 'message': '你没有权限'})

    def on_leave(self):
        token = request.headers.get('Authorization')
        if self.verify_token(token):
            user_id = self.verify_token(token)  # 获取用户的唯一标识符
            leave_room(user_id)  # 将用户从房间中移除
            emit('response', {'code': 200, 'message': '退出成功'})  # 发送消息给断开连接的用户
        else:
            emit('response', {'code': 400, 'message': '你没有权限'})

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
