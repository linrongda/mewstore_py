from flask import Blueprint
from flask_restful import Api

home_page_bp = Blueprint('home_page', __name__)
api = Api(home_page_bp)
# 导入和注册视图函数
from .homepage import HomePage
from .search import Search
from .guess import Guess
from .picture import Picture

api.add_resource(HomePage, '/home-page')
api.add_resource(Search, '/search')
api.add_resource(Guess, '/guess')
api.add_resource(Picture, '/picture')
