import sys

sys.path.append('../')  # '../'表示当前目录的父目录，也即这个项目的项目目录，引入环境变量，让python认为project是一个模块，终端下也可以使用

from flask import Flask

from project import config
from project.api import bp as api_bp
from project.exts import db, cors, socketio
from project.api.chat import Message

app = Flask(__name__)

# 导入配置
app.config.from_object(config)

# 导入扩展
db.init_app(app)  # 注册db
cors.init_app(app)  # 注册cors
socketio.init_app(app, cors_allowed_origins='*')  # 注册socketio，cors_allowed_origins='*'解决跨域问题
# csrf.init_app(app)  # csrf防御
# 注册蓝图
app.register_blueprint(api_bp)

socketio.on_namespace(Message('/chat'))  # 架构+蓝图的defuff下，只能在这里注册命名空间

if __name__ == '__main__':
    # app.run('0.0.0.0')
    socketio.run(app, host='0.0.0.0')  # 使用此语句即可
