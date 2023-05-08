from flask import Blueprint
from flask_restful import Api

users_bp = Blueprint('users', __name__)
api = Api(users_bp)
# 导入和注册视图函数
from .sms import Sms
api.add_resource(Sms, '/sms')
