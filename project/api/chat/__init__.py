from flask import Blueprint
from flask_restful import Api

chat_bp = Blueprint('chat', __name__)
api = Api(chat_bp)

from .message import Message
from .picture import Picture

api.add_resource(Picture, '/picture')
