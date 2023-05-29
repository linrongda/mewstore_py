from flask import Flask
from api import bp as api_bp
from exts import db, cors, socketio
import config
from project.api.chat import Message

app = Flask(__name__)

# 导入配置
app.config.from_object(config)

# 导入扩展
db.init_app(app)
cors.init_app(app)
socketio.init_app(app, cors_allowed_origins='*')
# 注册蓝图
app.register_blueprint(api_bp)

socketio.on_namespace(Message('/chat'))

if __name__ == '__main__':
    # app.run('0.0.0.0')
    socketio.run(app)
