# 配置日志功能
import logging

logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG)  # 设置日志级别为DEBUG
# 添加文件处理器
file_handler = logging.FileHandler(filename="app.log", encoding='utf-8')  # 创建日志处理器，用文件存放日志
# file_handler = logging.StreamHandler()  # 创建日志处理器，用控制台输出日志
file_handler.setLevel(logging.DEBUG)  # 设置日志处理器的日志级别为DEBUG
formatter = logging.Formatter("[%(asctime)s]-[%(levelname)s]-[%(filename)s]-[Line:%(lineno)d]-[Msg:%(message)s]")
file_handler.setFormatter(formatter)  # 设置日志处理器的日志格式
logger.addHandler(file_handler)  # 添加日志处理器
