FROM python:3-alpine

WORKDIR /app
COPY src .
RUN pip3 install -r requirements.txt

EXPOSE 80
ENV PORT=80

CMD ["python3", "__main__.py"]
