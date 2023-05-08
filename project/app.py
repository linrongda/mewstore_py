from flask import Flask
from api import bp as api_bp
from exts import db, cors
import config
app = Flask(__name__)

# 导入配置
app.config.from_object(config)

# 导入扩展
db.init_app(app)
cors.init_app(app)
# 注册蓝图
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run('0.0.0.0')
