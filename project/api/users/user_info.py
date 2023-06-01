from flask import request, make_response, jsonify
from flask_restful import Resource

from project.utils.auth import jwt_required, check_status
from project.utils.log import logger


class User_get(Resource):  # 获取用户信息
    @jwt_required
    @check_status([0, 1, 2, 3])
    def get(self):
        user = request.user
        # 隐藏用户真实姓名和身份证号码
        name = '*' * (len(user.name) - 1) + user.name[-1] if user.name else None
        id_card = user.id_card[0] + '*' * (len(user.id_card) - 2) + user.id_card[-1] if user.id_card else None
        user_info = {'id': user.id, 'nickname': user.nickname, 'username': user.username,
                     'profile_photo': user.profile_photo, 'phone_number': user.phone_number,
                     'money': user.money, 'status': user.status, 'name': name, 'id_card': id_card}
        logger.debug(f'用户{user.username}获取用户信息成功')
        return make_response(jsonify(code=200, message='获取用户信息成功', user=user_info), 200)
