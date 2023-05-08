from flask import Blueprint

bp = Blueprint('api', __name__)

# 导入和注册子蓝图
from .users import users_bp as users_bp
from .goods import goods_bp as goods_bp
from .home_page import home_page_bp as home_page_bp
from .b_s_center import b_s_center_bp as b_s_center_bp
bp.register_blueprint(users_bp, url_prefix='/users')
bp.register_blueprint(goods_bp, url_prefix='/goods')
bp.register_blueprint(home_page_bp)
bp.register_blueprint(b_s_center_bp, url_prefix='/users')
