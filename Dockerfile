FROM python:3-slim-buster

RUN apt update && apt install ffmpeg gcc -y

COPY *.py /app/
COPY requirements.txt /app/

RUN mkdir -p /app/cogs
COPY cogs/ /app/cogs/

RUN mkdir /app/data
RUN mkdir /app/data/temp

WORKDIR /app

RUN pip install -r requirements.txt && apt remove gcc -y && apt autoremove -y

CMD python chii.py