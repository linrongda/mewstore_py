from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
cors = CORS()
socketio = SocketIO()
csrf = CSRFProtect()
# def init_app(app):
#     db.init_app(app)
#     cors.init_app(app)
#     socketio.init_app(app)
