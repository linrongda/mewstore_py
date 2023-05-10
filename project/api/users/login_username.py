# 定义用户登录接口
from flask_restful import Resource, reqparse

from project.utils.auth import after_get_info


class Login_Username(Resource):
    def post(self):
        # 获取POST请求参数
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='请输入用户名')
        parser.add_argument('password', type=str, required=True, help='请输入密码')
        args = parser.parse_args()
        return after_get_info(args, login_type='username')
