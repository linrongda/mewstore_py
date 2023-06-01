import pytest

from project.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize('headers, data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU2NzkyMDUsImlhdCI6MTY4NTU5MjgwNSwiaWQiOjE2NTMzMDUzOTEyNjM2NDk3OTIsInN0YXR1cyI6MH0.lJjdI-pP9_cwEL4baFQfzRVvqF7NSMAnqPgaV2l3crk"
            },
            {"old_password": "123456", "password": "123456", "check_password": "123456"},
            201,
            {"code": 201, 'message': '修改密码成功'}
    ),
    (
            {
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU2NzkyMDUsImlhdCI6MTY4NTU5MjgwNSwiaWQiOjE2NTMzMDUzOTEyNjM2NDk3OTIsInN0YXR1cyI6MH0.lJjdI-pP9_cwEL4baFQfzRVvqF7NSMAnqPgaV2l3crk"
            },
            {"old_password": "123456", "password": "123456", "check_password": "654321"},
            400,
            {"code": 400, 'message': '两次输入的密码不一致'}
    ),
(
            {
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU2NzkyMDUsImlhdCI6MTY4NTU5MjgwNSwiaWQiOjE2NTMzMDUzOTEyNjM2NDk3OTIsInN0YXR1cyI6MH0.lJjdI-pP9_cwEL4baFQfzRVvqF7NSMAnqPgaV2l3crk"
            },
            {"old_password": "654321", "password": "123456", "check_password": "123456"},
            401,
            {"code": 401, 'message': '原密码错误'}
    )
])
def test_user_info(client, headers, data, expected_status_code, expected_response):
    response = client.put('/users/password', headers=headers, json=data, content_type='application/json')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
    assert response.json.get('user') == expected_response.get('user')
