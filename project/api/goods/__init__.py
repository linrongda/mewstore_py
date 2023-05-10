from flask import Blueprint
from flask_restful import Api

goods_bp = Blueprint('goods', __name__)
api = Api(goods_bp)
# # 导入和注册视图函数

