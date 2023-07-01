# 设置基础镜像
FROM python:3.9.13
# 设置代码文件夹工作目录 /app
WORKDIR /app
# 复制当前代码文件到容器中 /app
ADD . /app
# 设置时间
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# 安装所需的包，这里的requirements文件名需和项目生成的一致
RUN pip install --trusted-host mirrors.tuna.tsinghua.edu.cn -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/
# 执行入口文件
CMD ["python", "app.py"]
