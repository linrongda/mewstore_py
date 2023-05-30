from flask import Blueprint
from flask_restful import Api

chat_bp = Blueprint('chat', __name__)
api = Api(chat_bp)

from .message import Message
from .picture import Picture
from .read import MessageRead
from .history import MessageHistory

api.add_resource(Picture, '/picture')
api.add_resource(MessageRead, '/read')
api.add_resource(MessageHistory, '/history')
