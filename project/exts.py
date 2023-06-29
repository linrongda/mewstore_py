from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
# from flask_wtf.csrf import CSRFProtect
import redis

db = SQLAlchemy()
cors = CORS()
socketio = SocketIO()
# csrf = CSRFProtect()
redis = redis.StrictRedis(host="106.14.35.23", port=6379, db=0, password='114514', decode_responses=True)  # 连接redis
