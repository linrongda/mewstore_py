from flask import Blueprint
from flask_restful import Api

chat_bp = Blueprint('chat', __name__)
api = Api(chat_bp)

from .message import Message
from .read import MessageRead
from .history import MessageHistory
from .list import Chat_list

api.add_resource(MessageRead, '/read')
api.add_resource(MessageHistory, '/history')
api.add_resource(Chat_list, '/list')
