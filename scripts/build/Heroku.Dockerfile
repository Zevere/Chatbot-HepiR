FROM python:3-alpine

COPY app /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD python src/hepirbot.py
