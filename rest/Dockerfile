FROM python:3.9
LABEL MAINTAINER="lsw9128@gmail.com"

RUN usr/local/bin/python3.9 -m pip install --upgrade pip


RUN pip3 install flask
RUN pip3 install jsonpickle
RUN pip3 install requests
#RUN pip3 install socket
RUN pip3 install redis
RUN pip install cassandra-driver

RUN python3.9 -m pip install confluent_kafka

WORKDIR /srv

COPY rest-server.py /srv
ENV FLASK_APP=rest-server.py
CMD  python3 /srv/rest-server.py