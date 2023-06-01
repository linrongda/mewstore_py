import pytest
import json
from project.app import app  # 导入第三方包的时候报错no module？不急，pip重装解决


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


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
def test_login(client, data, expected_status_code, expected_response):
    response = client.post('/users/login/username', data=json.dumps(data), content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')

    if expected_status_code == 200:
        assert 'token' in response.json
        assert isinstance(response.json['token'], str)
