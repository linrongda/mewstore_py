from flask import Flask
from flask_cors import CORS

from user import user
# from good import good

app = Flask(__name__)
CORS(app)  # 实现跨域
app.register_blueprint(user)  # 注册蓝图
# app.register_blueprint(good)  # 注册蓝图

app.run(host='0.0.0.0')  # 内网可用
