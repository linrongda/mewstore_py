import pytest
from faker import Faker
from werkzeug.datastructures import MultiDict

from project.app import app  # 导入第三方包的时候报错no module？不急，pip重装解决

fake = Faker(locale='zh_CN')


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# @pytest.fixture(scope='session')
# def code(request):
#     # 在测试会话级别的缓存中存储 code
#     request.config.cache.set('code', None)
#
#
# @pytest.fixture(scope='session')
# def phone_number(request):
#     # 在测试会话级别的缓存中存储 phone_number
#     request.config.cache.set('phone_number', None)


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    # (
    #         {'phone_number': fake.phone_number(), 'type': 'register'},
    #         200,
    #         {"code": 200, 'message': '发送成功'}
    # ),
    # 测试重复注册同一用户的情况
    (
            {'phone_number': '12345678901', 'type': 'register'},
            400,
            {'code': 400, 'message': '请输入11位有效的手机号'}
    ),
    # 测试注册信息不完整的情况
    # (
    #         {'phone_number': fake.phone_number(), 'type': 'register'},
    #         400,
    #         {'code': 400, 'message': '请勿重复发送验证码'}
    # ),
    # (
    #         13333333333,
    #         400,
    #         {'code': 400, 'message': '发送失败'}
    # ),
    (
            {'phone_number': '13333333333', 'type': 'register'},
            400,
            {"code": 400, 'message': '该手机号已被注册'}
    ),
    (
            {'phone_number': '13456789012', 'type': 'login'},
            404,
            {"code": 404, 'message': '用户不存在'}
    ),
    (
            {'phone_number': '13333333333', 'type': 'modify'},
            400,
            {"code": 400, 'message': '该手机号已被使用'}
    )
])
def test_sms(client, data, expected_status_code, expected_response):
    response = client.post('/users/sms', json=data, content_type='application/json')
    # if response.status_code == 200:
    #     request.config.cache.set('phone_number', {'phone_number': data['phone_number']})
    #     request.config.cache.set('code', {'code': response.json['data']['code']})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response['code']
    assert response.json.get('message') == expected_response['message']


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    # (
    #         {
    #             "username": fake.user_name(),
    #             "password": None,
    #             "check_password": None,
    #         },
    #         201,
    #         {"code": 201, 'message': '注册成功'}
    # ),
    # 测试重复注册同一用户的情况
    (
            {
                "username": "user",
                "password": "password",
                "check_password": "password",
                "phone_number": "13333333333",
                "code": "123456"
            },
            400,
            {'code': 400, 'message': '用户名已存在'}
    ),
    # 测试注册信息不完整的情况
    # (
    #         {
    #             "username": "testuser",
    #             "password": "testpassword"
    #         },
    #         400,
    #         {'message': {'check_password': 'Missing required parameter in the JSON body or '
    #                                        'the post body or the query string'}}
    # )
    (
            {
                "username": "test",
                "password": "password",
                "check_password": "check_password",
                "phone_number": "13003808916",
                "code": "123456"
            },
            400,
            {'code': 400, 'message': '两次输入的密码不一致'}
    ),
    (
            {
                "username": "test",
                "password": "password",
                "check_password": "password",
                "phone_number": "15935746829",
                "code": "123456"
            },
            400,
            {'code': 400, 'message': '请先获取验证码'}
    ),
    # (
    #         {
    #             "username": "test",
    #             "password": "password",
    #             "check_password": "password",
    #             "code": "123456"
    #         },
    #         400,
    #         {'code': 400, 'message': '验证码错误'}
    # ),
])
def test_register(client, data, expected_status_code, expected_response):
    # if expected_status_code == 201:
    #     data['password'] = data['check_password'] = fake.password()
    #     data.update(request.config.cache.get('code', default=None))
    #     data.update(request.config.cache.get('phone_number', default=None))
    # if expected_status_code == 400 and expected_response['message'] == '验证码错误':
    #     data.update(request.config.cache.get('phone_number', default=None))
    response = client.post('/users', json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response['code']
    assert response.json.get('message') == expected_response['message']


@pytest.fixture(scope='session')
def token(request):
    # 在测试会话级别的缓存中存储 token
    request.config.cache.set('token', None)


@pytest.mark.parametrize('data, expected_status_code, expected_response', [

    (
            {
                "phone_number": "15935746829",
                "code": "123456"
            },
            400,
            {'code': 400, 'message': '请先获取验证码'}
    ),
    # (
    #         {
    #             "username": "test",
    #             "password": "password",
    #             "check_password": "password",
    #             "code": "123456"
    #         },
    #         400,
    #         {'code': 400, 'message': '验证码错误'}
    # ),
    (
            {'phone_number': '12345678901', 'code': '666666'},
            400,
            {'code': 400, 'message': '请输入11位有效的手机号'}
    )
    # (
    #         {'phone_number': '13456789012', 'code': '666666'},
    #         404,
    #         {"code": 404, 'message': '用户不存在'}
    # )
])
def test_login_phone(client, data, expected_status_code, expected_response):
    # if expected_status_code == 201:
    #     data.update(request.config.cache.get('code', default=None))
    #     data.update(request.config.cache.get('phone_number', default=None))
    # if expected_status_code == 400 and expected_response['message'] == '验证码错误':
    #     data.update(request.config.cache.get('phone_number', default=None))
    response = client.post('/users/login/phone', json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response['code']
    assert response.json.get('message') == expected_response['message']


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {
                "username": "user",
                "password": "123456"
            },
            200,
            {"code": 200, 'message': '登录成功'}
    ),
    # 测试重复注册同一用户的情况
    (
            {
                "username": "testuser",
                "password": "testpassword"
            },
            401,
            {'code': 401, 'message': '用户名或密码错误'}
    )
])
def test_login_username(client, data, expected_status_code, expected_response, token, request):
    response = client.post('/users/login/username', json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')

    if expected_status_code == 200:
        assert 'token' in response.json
        request.config.cache.set('token', {"Authorization": response.json['token']})
        assert isinstance(response.json['token'], str)


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取用户信息成功', 'user': {"id": 1653305391263649792,
                                                                  "id_card": '6****************6',
                                                                  "money": "3778.00",
                                                                  "name": '***r',
                                                                  "nickname": 'user',
                                                                  "phone_number": "1*********3",
                                                                  "profile_photo": "http://qiniuyun.mewtopia.cn/FgQuh8Z8hTTTHt4pMtSlsiugZfHk",
                                                                  "status": 0,
                                                                  "username": "user"}}
    )
])
def test_user_info(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/users', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
    assert response.json.get('user') == expected_response.get('user')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"username": "user"},
            400,
            {"code": 400, 'message': '该用户名已存在'}
    )
])
def test_user_username(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/users/username', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"nickname": "user"},
            201,
            {"code": 201, 'message': '修改昵称成功'}
    )
])
def test_user_nickname(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/users/nickname', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"old_password": "123456", "password": "123456", "check_password": "123456"},
            201,
            {"code": 201, 'message': '修改密码成功'}
    ),
    (
            {"old_password": "123456", "password": "123456", "check_password": "654321"},
            400,
            {"code": 400, 'message': '两次输入的密码不一致'}
    ),
    (
            {"old_password": "654321", "password": "123456", "check_password": "123456"},
            401,
            {"code": 401, 'message': '原密码错误'}
    )
])
def test_user_password(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/users/password', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            MultiDict([
                ('profile_photo', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            201,
            {"code": 201, 'message': '修改头像成功'}
    )
])
def test_user_profile_photo(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/users/profile-photo', headers=headers, data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"money": 99999, "type": "recharge"},
            201,
            {"code": 201, 'message': '充值成功'}
    ),
    # 测试余额不足的情况
    (
            {"money": 99999, "type": "withdrawal"},
            201,
            {"code": 201, 'message': '提现成功'})
])
def test_user_money(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/users/money', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"name": 'name', "id_card": "123456789012345678"},
            400,
            {"code": 400, 'message': '请输入18位正确的身份证号'}
    ),
    # 测试余额不足的情况
    (
            {"name": 'user', "id_card": "666666206606066666"},
            400,
            {"code": 400, 'message': '你已经实名认证过了'})
])
def test_rna(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/users/real-name-authentication', headers=headers, json=data,
                          content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [

    (
            {
                "phone_number": "15935746829",
                "code": "123456"
            },
            400,
            {'code': 400, 'message': '请先获取验证码'}
    ),
    # (
    #         {
    #             "username": "test",
    #             "password": "password",
    #             "check_password": "password",
    #             "code": "123456"
    #         },
    #         400,
    #         {'code': 400, 'message': '验证码错误'}
    # ),
    (
            {'phone_number': '12345678901', 'code': '666666'},
            400,
            {'code': 400, 'message': '请输入11位有效的手机号'}
    ),
    (
            {'phone_number': '13333333333', 'code': '666666'},
            400,
            {"code": 400, 'message': '该手机号已被使用'}
    )
])
def test_user_phone_number(client, data, expected_status_code, expected_response, request):
    headers = request.config.cache.get('token', default=None)
    # if expected_status_code == 201:
    #     data.update(request.config.cache.get('code', default=None))
    #     data.update(request.config.cache.get('phone_number', default=None))
    # if expected_status_code == 400 and expected_response['message'] == '验证码错误':
    #     data.update(request.config.cache.get('phone_number', default=None))
    response = client.put('/users/phone-number', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response['code']
    assert response.json.get('message') == expected_response['message']


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            MultiDict([
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            201,
            {"code": 201, 'message': '上传图片成功', 'data': 'http://qiniuyun.mewtopia.cn/FgQuh8Z8hTTTHt4pMtSlsiugZfHk'}
    )
])
def test_chat_picture(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.post('/chat/picture', headers=headers, data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
    assert response.json.get('data') == expected_response.get('data')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取成功'}
    )
])
def test_chat_history(client, expected_status_code, expected_response, token, request):
    headers = {'send_id': '1653305391263649792'}
    header = request.config.cache.get('token', default=None)
    headers.update(header)
    response = client.get('/chat/history', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"send_id": '1652948308014010368', "message_id": "1337400298553102336"},
            404,
            {"code": 404, 'message': '消息不存在或已读'}
    )
])
def test_chat_read(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.put('/chat/read', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取消息列表成功'}
    )
])
def test_chat_list(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/chat/list', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取商品信息成功'}
    )
])
def test_good_info(client, expected_status_code, expected_response):
    response = client.get('/goods/1654432305042825216')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.fixture(scope='session')
def good_id(request):
    # 在测试会话级别的缓存中存储 good_id
    request.config.cache.set('good_id', None)


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            MultiDict([
                ('price', '666.0'),
                ('title', fake.word()),
                ('content', fake.text()),
                ('game', fake.word()),
                ('account', fake.email()),
                ('password', fake.password()),
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb')),
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            201,
            {"code": 201, 'message': '创建商品信息成功'}
    ),
    (
            MultiDict([
                ('price', '666.0'),
                ('title', 'test6'),
                ('content', 'test6'),
                ('game', 'test6'),
                ('account', 'test6'),
                ('password', 'test6'),
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            400,
            {"code": 400, 'message': '商品已存在'}
    )
])
def test_good_add(client, data, expected_status_code, expected_response, token, good_id, request):
    headers = request.config.cache.get('token', default=None)
    response = client.post('/goods', headers=headers, data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status_code
    if response.status_code == 201:
        request.config.cache.set('good_id', {"id": response.json['data']['id']})
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            204,
            {"code": 204, 'message': '删除商品成功'}
    ),
    (
            404,
            {"code": 404, 'message': '商品不存在'}
    )
])
def test_good_delete(client, expected_status_code, expected_response, token, good_id, request):
    headers = request.config.cache.get('token', default=None)
    data = request.config.cache.get('good_id', default=None)
    response = client.delete('/goods', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    if response.status_code == 404:
        assert response.json.get('code') == expected_response.get('code')
        assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            MultiDict([
                ('id', '1654432305042825216'),
                ('price', '666.0'),
                ('title', 'test6'),
                ('content', 'test6'),
                ('game', 'test6'),
                ('account', 'test6'),
                ('password', 'test6'),
                ('status', '1'),
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb')),
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            201,
            {"code": 201, 'message': '修改商品信息成功'}
    )
])
def test_good_update(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.patch('/goods', headers=headers, data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '查询收藏的商品成功'}
    )
])
def test_favorite_get(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/users/favorites', headers=headers, query_string={'page': 1, 'size': 4})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {"good_id": "1654432305042825216"},
            400,
            {"code": 400, 'message': '已收藏'}
    )
])
def test_favorite_add(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.post('/users/favorites', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取出售商品成功'}
    )
])
def test_sell(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/users/goods', headers=headers, query_string={'page': 1, 'size': 4})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取猜你喜欢商品成功'}
    )
])
def test_guess(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/guess', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取首页商品成功'}
    )
])
def test_homepage(client, expected_status_code, expected_response):
    response = client.get('/home-page', query_string={'page': 1, 'size': 4})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取搜索商品成功'}
    )
])
def test_search(client, expected_status_code, expected_response):
    response = client.get('/search', query_string={'page': 1, 'size': 4, 'keywords': ''})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
