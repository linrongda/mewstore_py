from flask import Blueprint
from flask_restful import Api

b_s_center_bp = Blueprint('b_s_center', __name__)
api = Api(b_s_center_bp)
# 导入和注册视图函数
from .favorite_add import Favorite_add
from .favorite_get import Favorite_get
from .sell import Sell

api.add_resource(Favorite_add, '/favorites')
api.add_resource(Favorite_get, '/favorites')
api.add_resource(Sell, '/goods')
