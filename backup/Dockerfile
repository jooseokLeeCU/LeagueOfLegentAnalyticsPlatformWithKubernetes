FROM python:3.9

LABEL MAINTAINER="lsw9128@gmail.com"

RUN pip install --upgrade pip
RUN pip install redis
RUN pip3 install mysql-connector-python==8.0.29
RUN pip3 install minio
RUN pip install numpy
RUN pip install pandas


WORKDIR /app
COPY    backup.py /app

ENTRYPOINT [ "python3", "backup.py"]