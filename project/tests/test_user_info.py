import pytest

from project.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize('headers, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU2NzkyMDUsImlhdCI6MTY4NTU5MjgwNSwiaWQiOjE2NTMzMDUzOTEyNjM2NDk3OTIsInN0YXR1cyI6MH0.lJjdI-pP9_cwEL4baFQfzRVvqF7NSMAnqPgaV2l3crk"
            },
            200,
            {"code": 200, 'message': '获取用户信息成功', 'user': {"id": 1653305391263649792,
                                                                  "id_card": None,
                                                                  "money": "3778.00",
                                                                  "name": None,
                                                                  "nickname": 'user',
                                                                  "phone_number": "13333333333",
                                                                  "profile_photo": "http://qiniuyun.mewtopia.cn/FgQuh8Z8hTTTHt4pMtSlsiugZfHk",
                                                                  "status": 0,
                                                                  "username": "user"}}
    )
])
def test_user_info(client, headers, expected_status_code, expected_response):
    response = client.get('/users', headers=headers)
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
    assert response.json.get('user') == expected_response.get('user')
