FROM crpi-x1nkaf6h1u17ptla.cn-chengdu.personal.cr.aliyuncs.com/wexyzx_space/python:3.10-slim-buster
LABEL maintainer="1090349183@qq.com"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD [ "python3" , "server.py" ]
