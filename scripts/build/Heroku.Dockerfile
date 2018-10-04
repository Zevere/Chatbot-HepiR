FROM python:3-alpine

COPY app /app
WORKDIR /app

RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
RUN pip install -r requirements.txt

CMD python hepirbot.py
