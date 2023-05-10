from flask import Blueprint
from flask_restful import Api

users_bp = Blueprint('users', __name__)
api = Api(users_bp)
# 导入和注册视图函数
from .sms import Sms
from .register import Register
from .login_username import Login_Username
from .login_phone import Login_Phone
from .user_info import User_get
from .user_nickname import User_nickname
from .user_username import User_username
from .user_password import User_password
from .user_profile_photo import User_profile_photo
from .user_phone_number import User_phone_number
from .user_money import User_money
from .real_name_auth import Real_name_authentication

api.add_resource(Sms, '/sms')
api.add_resource(Register, '/')
api.add_resource(Login_Username, '/login/username')
api.add_resource(Login_Phone, '/login/phone')
api.add_resource(User_get, '/')
api.add_resource(User_nickname, '/nickname')
api.add_resource(User_username, '/username')
api.add_resource(User_password, '/password')
api.add_resource(User_profile_photo, '/profile-photo')
api.add_resource(User_phone_number, '/phone-number')
api.add_resource(User_money, '/money')
api.add_resource(Real_name_authentication, '/real-name-authentication')
