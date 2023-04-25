from flask import jsonify, Flask
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
from data import db, app, User

# user = data.User(nickname=11, password=22)
# data.session.add(user)
# data.session.commit()
# good = data.Good(view=1, content=2, game=3, title=4, account=5, password=6, status=7, sell_id=8)
# data.session.add(good)
# data.session.commit()
# def test():
#     return jsonify(code=404, message=f'登录失败'), 200
# with app.app_context():
#     try:
#         if test().index(200):
#             print('success')
#     except Exception as e:
#         print('error')
#
#     print(type(jsonify(code=404, message=f'登录失败')))
with app.app_context():
    a = db.session.query(User).get(1)
    print(a)
# class User():
#     def __init__(self):
#         self.user = data.session.query(data.User).get(1)
#     def get(self):
#         print(self.user)
#
# User().get()
# class good():
#     def __init__(self):
#         self.good = data.session.query(data.Good).get(1)
#     def get(self):
#         self.good.view += 1
#         data.session.commit()
#         print(self.good)
# good().get()
# from user import check_password,password_encrypt
# a = password_encrypt('123456789dfsfsdvrgv')
# print(a)
# print(check_password('pbkdf2:sha256:260000$fHs4YPAT3LyOfZBo$78927d3394798f298e0c8fa5a287499570dfe5388497d17eeb996acbcde662c1', '123456'))
