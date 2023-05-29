from flask import Blueprint
from flask_restful import Api

chat_bp = Blueprint('chat', __name__)
api = Api(chat_bp)
