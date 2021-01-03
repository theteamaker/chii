FROM python:3-slim-buster

RUN apt update && apt install ffmpeg -y

COPY *.py /app/
COPY requirements.txt /app/

RUN mkdir -p /app/cogs
COPY cogs/ /app/cogs/

RUN mkdir /app/data

WORKDIR /app

RUN pip install -r requirements.txt && apt autoremove -y

CMD python chii.py