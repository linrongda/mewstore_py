from flask import request, make_response, jsonify
from flask_restful import Resource

from project.models import User, db
from project.utils.auth import jwt_required
from project.utils.log import logger


class User_get(Resource):
    @jwt_required
    def get(self):
        # with app.app_context():
        user = db.session.query(User).get(request.payload_id)
        if user and user.status in range(0, 4):
            if user.profile_photo:
                profile_photo_url = 'http://rtqcx0dtq.bkt.clouddn.com/' + user.profile_photo
            else:
                profile_photo_url = None
                name = '*' * (len(user.name) - 1) + user.name[-1] if user.name else None
                id_card = user.id_card[0] + '*' * (len(user.id_card) - 2) + user.id_card[
                    -1] if user.id_card else None
            user_info = {'id': user.id, 'nickname': user.nickname, 'username': user.username,
                         'profile_photo': profile_photo_url, 'phone_number': user.phone_number,
                         'money': user.money, 'status': user.status, 'name': name, 'id_card': id_card}
            logger.debug('获取用户信息成功')
            return make_response(jsonify(code=200, message='获取用户信息成功', user=user_info), 200)
        else:
            return make_response(jsonify(code=403, message='你没有权限'), 403)
