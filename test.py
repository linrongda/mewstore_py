from flask import jsonify, Flask

app = Flask(__name__)
import data
# user = data.User(nickname=1, password=2)
# data.session.add(user)
# data.session.commit()
def test():
    return jsonify(code=404, message=f'登录失败'), 200
with app.app_context():
    try:
        if test().index(200):
            print('success')
    except Exception as e:
        print('error')

    print(type(jsonify(code=404, message=f'登录失败')))