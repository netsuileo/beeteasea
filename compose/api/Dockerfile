FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y wait-for-it gcc
RUN apt-get clean
COPY ./ /app
WORKDIR /app
RUN pip install -r requirements.txt
