from flask import Flask
from flask_cors import CORS
from api.user import user
from api.good import good
from api.b_s_center import b_s_center
from api.home_page import home_page

app = Flask(__name__)
app.secret_key = 'mewstore'
CORS(app)  # 实现跨域
app.register_blueprint(user)  # 注册蓝图
app.register_blueprint(good)  # 注册蓝图
app.register_blueprint(b_s_center)  # 注册蓝图
app.register_blueprint(home_page)  # 注册蓝图

import logging

logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)  # 设置日志级别为DEBUG
# 添加文件处理器
file_handler = logging.FileHandler(filename="app.log",encoding='utf-8')  # 创建日志处理器，用文件存放日志
# file_handler = logging.StreamHandler()  # 创建日志处理器，用控制台输出日志
file_handler.setLevel(logging.DEBUG)  # 设置日志处理器的日志级别为DEBUG
formatter = logging.Formatter("[%(asctime)s]-[%(levelname)s]-[%(filename)s]-[Line:%(lineno)d]-[Msg:%(message)s]")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app.run(host='0.0.0.0')  # 内网可用
