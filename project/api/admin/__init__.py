from flask import Blueprint
from flask_restful import Api

admin_bp = Blueprint('admin', __name__)
api = Api(admin_bp)
# # 导入和注册视图函数

from .admin_goods import Admin_goods


api.add_resource(Admin_goods, '/goods')
