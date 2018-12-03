FROM python:3-alpine as base
WORKDIR /app
COPY src .
RUN pip3 install -r requirements.txt


FROM base as final
EXPOSE 80
ENV PORT=80
CMD ["python3", "__main__.py"]


FROM base as test
COPY tests .
RUN pip3 install -r requirements-test.txt
CMD ["pytest", "--verbose", "--disable-warnings"]