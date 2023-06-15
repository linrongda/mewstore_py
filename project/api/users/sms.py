import datetime
import random
import re

from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from flask import jsonify, make_response, session
from flask_restful import Resource, reqparse

from project.models import User
from project.models import db
from project.utils.aes import encrypt
from project.utils.log import logger
from project.utils.send_sms import Sample


class Sms(Resource):  # 获取短信验证码
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('phone_number', type=str, required=True, help='请输入手机号')
        parser.add_argument('type', type=str, required=True, help='请输入验证类型')
        args = parser.parse_args()
        if args['type'] not in ['register', 'login', 'modify']:
            return make_response(jsonify(code=400, message='type参数错误'), 400)
        if not bool(re.match(r'^1[3-9]\d{9}$', args['phone_number'])):
            return make_response(jsonify(code=400, message='请输入11位有效的手机号'), 400)
        if args['type'] == 'register':
            if User.query.filter_by(phone_number=encrypt(args['phone_number'])).first():
                return make_response(jsonify(code=400, message='该手机号已被注册'), 400)
        if args['type'] == 'login':
            if not db.session.query(User).filter_by(phone_number=encrypt(args['phone_number'])).first():
                return make_response(jsonify(code=404, message='用户不存在'), 404)
        if args['type'] == 'modify':
            if User.query.filter_by(phone_number=encrypt(args['phone_number'])).first():
                return make_response(jsonify(code=400, message='该手机号已被使用'), 400)
        if session.get(f'{args["phone_number"]}') and \
                session[f'{args["phone_number"]}_time'].replace(tzinfo=None) > datetime.datetime.utcnow():
            return make_response(jsonify(code=400, message='请勿重复发送验证码'), 400)
        else:
            code = ''.join(random.choices('0123456789', k=6))
            client = Sample.create_client(access_key_id='LTAI5tNVqQ16EgH2Xn6fxar1',
                                          access_key_secret='eIm61r1Uy8e5IDjDepBN3JKiqXmLeO')
            send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
                sign_name='闲猫MewStore',
                template_code='SMS_460685295',
                phone_numbers=args["phone_number"],
                template_param='{"code":"%s"}' % code
            )
            runtime = util_models.RuntimeOptions()
            try:
                # 复制代码运行请自行打印 API 的返回值
                response = client.send_sms_with_options(send_sms_request, runtime)
                if response.body.code == 'OK':
                    session[f'{args["phone_number"]}'] = code
                    session[f'{args["phone_number"]}_time'] = \
                        datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
                    logger.debug(f'手机号{args["phone_number"]}发送验证码成功')
                    return make_response(jsonify(code=200, message='发送成功'), 200)
                else:
                    return make_response(jsonify(code=400, message='发送失败'), 400)
            except Exception as error:
                # 如有需要，请打印 error
                return make_response(jsonify(code=400, message=f'发生未知错误：{error}'), 400)
