import pytest

import requests


def photo():
    with open('C:/Users/Administrator/Desktop/t.png', 'rb') as f:
        return f.read()


@pytest.mark.parametrize('headers, data, expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            {
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU2NzkyMDUsImlhdCI6MTY4NTU5MjgwNSwiaWQiOjE2NTMzMDUzOTEyNjM2NDk3OTIsInN0YXR1cyI6MH0.lJjdI-pP9_cwEL4baFQfzRVvqF7NSMAnqPgaV2l3crk"
            },
            {"profile_photo": photo()},
            201,
            {"code": 201, 'message': '修改头像成功'}
    )
])
def test_user_info(headers, data, expected_status_code, expected_response):
    response = requests.put('http://127.0.0.1:5000/users/profile-photo', headers=headers, files=data)
    assert response.status_code == expected_status_code
    assert response.json().get('code') == expected_response.get('code')
    assert response.json().get('message') == expected_response.get('message')
    assert response.json().get('user') == expected_response.get('user')
