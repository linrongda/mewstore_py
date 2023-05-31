DEBUG = True  # 开启调试模式
SECRET_KEY = 'mewstore'  # flask的app密钥

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://mew_store:114514@106.14.35.23:3306/test'  # 数据库连接
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 跟踪修改，必须有这个，要不然必报错，找了半天才发现
