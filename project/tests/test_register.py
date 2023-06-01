#
# import pytest
# import json
# from project.app import app
#
#
# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client
#
#
# # @pytest.mark.parametrize('data, expected_status_code, expected_response', [
# #     # 测试成功注册的情况
# #     (
# #             13003808916,
# #             200,
# #             {"code": 200, 'message': '发送成功'}
# #     ),
# #     # 测试重复注册同一用户的情况
# #     (
# #             12345678901,
# #             400,
# #             {'code': 400, 'message': '请输入11位有效的手机号'}
# #     ),
# #     # 测试注册信息不完整的情况
# #     (
# #             13003808916,
# #             400,
# #             {'code': 400, 'message': '请勿重复发送验证码'}
# #     ),
# #     (
# #             13333333333,
# #             400,
# #             {'code': 400, 'message': '发送失败'}
# #     ),
# #
# # ])
# # def test_sms(client, data, expected_status_code, expected_response):
# #     response = client.get('/sms/%s' % data)
# #     assert response.status_code == expected_status_code
# #     assert response.json == expected_response
#
#
# @pytest.mark.parametrize('data, expected_status_code, expected_response', [
#     # 测试成功注册的情况
#     (
#             {
#                 "username": "user",
#                 "password": "password",
#                 "check_password": "password",
#                 "phone_number": "13003808916",
#                 "code": "123456"
#             },
#             201,
#             {"code": 201, 'message': '注册成功'}
#     ),
#     # 测试重复注册同一用户的情况
#     (
#             {
#                 "username": "user",
#                 "password": "password",
#                 "check_password": "password",
#                 "phone_number": "13003808916",
#                 "code": "123456"
#             },
#             400,
#             {'code': 400, 'message': '用户名已存在'}
#     ),
#     # 测试注册信息不完整的情况
#     # (
#     #         {
#     #             "username": "testuser",
#     #             "password": "testpassword"
#     #         },
#     #         400,
#     #         {'message': {'check_password': 'Missing required parameter in the JSON body or '
#     #                                        'the post body or the query string'}}
#     # )
# ])
# def test_register(client, data, expected_status_code, expected_response):
#     response = client.post('/users', data=json.dumps(data), content_type='application/json')
#     assert response.status_code == expected_status_code
#     assert response.json == expected_response