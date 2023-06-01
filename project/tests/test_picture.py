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
            {"picture": photo()},
            201,
            {"code": 201, 'message': '上传图片成功', 'data': 'http://qiniuyun.mewtopia.cn/FgQuh8Z8hTTTHt4pMtSlsiugZfHk'}
    )
])
def test_user_info(headers, data, expected_status_code, expected_response):
    response = requests.post('http://127.0.0.1:5000/chat/picture', headers=headers, files=data)
    assert response.status_code == expected_status_code
    assert response.json().get('code') == expected_response.get('code')
    assert response.json().get('message') == expected_response.get('message')
    assert response.json().get('data') == expected_response.get('data')