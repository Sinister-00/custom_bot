FROM python:3.8-slim-buster


RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 6969
WORKDIR /app

COPY requirements.txt requirements.txt
COPY . /app

RUN pip3 install -r requirements.txt

CMD [ "streamlit","run","main.py","--server.port","6969" ]
