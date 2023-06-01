import pytest
import requests
from werkzeug.datastructures import MultiDict

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
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODU2NzkyMDUsImlhdCI6MTY4NTU5MjgwNSwiaWQiOjE2NTMzMDUzOTEyNjM2NDk3OTIsInN0YXR1cyI6MH0.lJjdI-pP9_cwEL4baFQfzRVvqF7NSMAnqPgaV2l3crk",
                "Content-Type": "multipart/form-data"
            },
            MultiDict([
                ('id', '1654432305042825216'),
                ('price', '666.0'),
                ('title', 'test6'),
                ('content', 'test6'),
                ('game', 'test6'),
                ('account', 'test6'),
                ('password', 'test6'),
                ('status', '1'),
                ('picture', open('C:/Users/Administrator/Desktop/t.png', 'rb'))
            ]),
            201,
            {"code": 201, 'message': '修改商品信息成功'}
    )
])
def test_user_info(client, headers, data, expected_status_code, expected_response):
    response = client.patch('/goods', headers=headers, data=data, content_type='multipart/form-data')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
