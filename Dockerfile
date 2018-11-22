FROM python:3-alpine

WORKDIR /app
COPY src ./src
RUN pip3 install -r src/requirements.txt

EXPOSE 80
ENV PORT=80

CMD ["python3", "src/hepirbot.py"]
