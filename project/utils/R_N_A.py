import json

import requests


def r_n_a(name, id_card):
    url = 'http://eid.shumaidata.com/eid/check'
    params = {
        'idcard': id_card,
        'name': name
    }
    headers = {
        'Authorization': 'APPCODE 7740e015b9c1430b9c74d592f1153bdb'
    }
    # 发送请求并获取响应
    response = requests.post(url, params=params, headers=headers)
    # 解析响应并返回结果
    result = json.loads(response.text)
    if result['result']['res'] == '1':
        return True
    else:
        return False
