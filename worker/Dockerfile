FROM python:3.9

LABEL MAINTAINER="lsw9128@gmail.com"

RUN pip install --upgrade pip
RUN pip install redis
RUN pip install numpy
RUN pip install pandas
RUN pip3 install mysql-connector-python==8.0.29
RUN pip3 install riotwatcher
RUN python3.9 -m pip install confluent_kafka
RUN pip install cassandra-driver

WORKDIR /app
COPY    worker-R1-server.py /app

ENTRYPOINT [ "python3", "worker-R1-server.py"]