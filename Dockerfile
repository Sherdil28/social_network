FROM python:3.12.4
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get install -y default-libmysqlclient-dev
ENV PYTHONUNBUFFERED 1
RUN mkdir /social_network
WORKDIR /social_network
COPY requirements.txt /social_network/
RUN pip install -r requirements.txt
RUN apt-get update
COPY . /social_network/