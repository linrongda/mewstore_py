from flask import Blueprint
from flask_restful import Api

goods_bp = Blueprint('goods', __name__)
api = Api(goods_bp)
# # 导入和注册视图函数
from .good_info import Good_get
from .good_add import Good_add
from .good_update import Good_update

api.add_resource(Good_get, '')
api.add_resource(Good_add, '')
api.add_resource(Good_update, '')
