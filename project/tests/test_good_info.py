import pytest

from project.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.parametrize('expected_status_code, expected_response', [
    # 测试成功注册的情况
    (
            200,
            {"code": 200, 'message': '获取商品信息成功'}
    )
])
def test_user_info(client, expected_status_code, expected_response):
    response = client.get('/goods/1654432305042825216')
    assert response.status_code == expected_status_code
    assert response.json.get('code') == expected_response.get('code')
    assert response.json.get('message') == expected_response.get('message')
