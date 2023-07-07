import pytest
from faker import Faker
from werkzeug.datastructures import MultiDict

from project.app import app  # 导入第三方包的时候报错no module？不急，pip重装解决

fake = Faker(locale='zh_CN')  # 生成虚假的随机数据，具体用法自行搜索


# 以下测试均在命令行使用 pytest --cov 测试覆盖率，pycharm中测试可能会出现导入路径问题

# 配置pytest应用
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


"""
由于pytest为每个接口单独测试，
故无法很好地使用flask应用中的session功能，
后端中所有与跨接口session存储和读取有关的代码均无法正常发挥作用。

而我的后端对验证码的存储和读取均使用了session，
所以在测试时无法正常使用验证码功能，已弃用。
"""

# @pytest.fixture(scope='session')
# def code(request):
#     # 在测试会话级别的缓存中存储 code
#     request.config.cache.set('code', None)
"""
注意！“scope='session'”为在整个测试会话中缓存，与flask应用中的session不同。注意区分。

set()方法用于存储数据，get()方法用于读取数据。get要有default=None哦，不然会报错。
使用这个缓存，通过设计良好的接口测试顺序，可以实现一定程度上的自动化测试。
例如：登录获取token并存储，之后的接口测试都可以使用这个token。

"""
#
# @pytest.fixture(scope='session')
# def phone_number(request):
#     # 在测试会话级别的缓存中存储 phone_number
#     request.config.cache.set('phone_number', None)


"""
！！！
！！！测试用法说明：'data, expected_status_code, expected_response'为需要传入的参数以及断言所需参数，可自定义，
！！！使用列表来存储多个测试用例，每个测试用例为一个元组，元组中的元素为测试用例的参数。
！！！其他具体用法可以分析下面每个接口测试之间的差异。例如get、post、put、delete等用法。
！！！还有不懂得可以上网搜或chatGPT。
！！！json=data可以自动帮你把数据格式化为json，而content_type必不可少哦。cv工程师？那就无脑搬吧！
！！！怎么传表单数据？见350行，多数据见533行
！！！
"""


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    # (
    #         {'phone_number': fake.phone_number(), 'type': 'register'},
    #         200,
    #         {"code": 200, 'message': '发送成功'}
    # ),
    (
            {'phone_number': '12345678901', 'type': 'register'},
            400,
            {'code': 400, 'message': '请输入11位有效的手机号'}
    ),
    # (
    #         {'phone_number': None, 'type': 'register'},
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
                "username": "tuser",
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
                "phone_number": "13333333333",
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
                "phone_number": fake.phone_number(),
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
    # )
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
    # (
    #         {
    #             "phone_number": None,
    #             "code": None
    #         },
    #         200,
    #         {'code': 200, 'message': '登录成功'}
    # ),
    (
            {
                "phone_number": fake.phone_number(),
                "code": "123456"
            },
            400,
            {'code': 400, 'message': '请先获取验证码'}
    ),
    # (
    #         {
    #             "phone_number": None,
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
    # if expected_status_code == 200:
    #     data.update(request.config.cache.get('code', default=None))
    #     data.update(request.config.cache.get('phone_number', default=None))
    # if expected_status_code == 400 and expected_response['message'] == '验证码错误':
    #     data.update(request.config.cache.get('phone_number', default=None))
    response = client.post('/users/login/phone', json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response['code']
    assert response.json.get('message') == expected_response['message']


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    (
            {
                "username": "tuser",
                "password": "123456"
            },
            200,
            {"code": 200, 'message': '登录成功'}
    ),
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
    (
            200,
            {"code": 200, 'message': '获取用户信息成功'}
    )
])
def test_user_info(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/users', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    (
            {"username": "tuser"},
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
    (
            {"nickname": "tuser"},
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
    (  # 你居然能够看到这里！注意哦，传入图片等需要使用表单，这里需要使用MultiDict，并使用data=data, content_type='multipart/form-data'
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
    (
            {"money": 99999, "type": "recharge"},
            201,
            {"code": 201, 'message': '充值成功'}
    ),
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
    (
            {"name": 'name', "id_card": "123456789012345678"},
            400,
            {"code": 400, 'message': '请输入18位正确的身份证号'}
    ),
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
                "phone_number": fake.phone_number(),
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
    (
            MultiDict([
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            201,
            {"code": 201, 'message': '上传图片成功'}
    )
])
def test_picture(client, data, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.post('/picture', headers=headers, data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('expected_status_code, expected_response', [
    (
            200,
            {"code": 200, 'message': '获取成功'}
    )
])
def test_chat_history(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('/chat/history', headers=headers, query_string={'send_id': '1652948308014010368'})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
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
    (
            200,
            {"code": 200, 'message': '获取商品信息成功'}
    )
])
def test_good_info(client, expected_status_code, expected_response):
    response = client.get('/goods', query_string={'id': '1654432305042825216'})
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')


@pytest.fixture(scope='session')
def good_id(request):
    # 在测试会话级别的缓存中存储 good_id
    request.config.cache.set('good_id', None)


@pytest.mark.parametrize('data, expected_status_code, expected_response', [
    (  # 哟，来啦
            MultiDict([
                ('price', '666.0'),
                ('title', fake.word()),
                ('content', fake.text()),
                ('game', fake.word()),
                ('account', fake.email()),
                ('password', fake.password()),
                ('picture', 'http://qiniuyun.mewtopia.cn/FgQuh8Z8hTTTHt4pMtSlsiugZfHk')
            ]),
            201,
            {"code": 201, 'message': '创建商品信息成功'}
    ),
    (
            MultiDict([
                ('price', '666.0'),
                ('title', '崩坏自抽初始号国服官服'),
                ('content', '账号等级:35级(220抽) 星琼数量:13000-14000 普票:95+张 专票:20+张'),
                ('game', '崩坏:星穹铁道'),
                ('account', '111111'),
                ('password', 'test6'),
                ('picture', 'http://qiniuyun.mewtopia.cn/FpUvj43w9GCj6o5oMCogUbkp9nIC')
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
    (
            MultiDict([
                ('id', '1654432305042825216'),
                ('price', '666.0'),
                ('title', '崩坏自抽初始号国服官服'),
                ('content', '账号等级:35级(220抽) 星琼数量:13000-14000 普票:95+张 专票:20+张'),
                ('game', '崩坏:星穹铁道'),
                ('account', '111111'),
                ('password', 'test6'),
                ('status', '1'),
                ('picture', 'http://qiniuyun.mewtopia.cn/FpUvj43w9GCj6o5oMCogUbkp9nIC')
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


@pytest.mark.parametrize('expected_status_code, expected_response', [
    (
            200,
            {"code": 200, 'message': '获取商品成功'}
    )
])
def test_admin_goods(client, expected_status_code, expected_response, token, request):
    headers = request.config.cache.get('token', default=None)
    response = client.get('admin/goods', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')