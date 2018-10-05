# Using the official python runtime base image
#FROM python:3.7
FROM python:3.7-alpine
MAINTAINER Kevin Ma

# Set the application directory
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install our requirements
ADD src/requirements.txt $APP_HOME/requirements.txt
RUN pip install -r requirements.txt

# Copy our code from the current folder to /app inside the container
COPY . $APP_HOME

# Install nodemon for hot reloading of .py files
# The package nodejs is no longer installing NPM (see pkgs.alpinelinux.org) You have to install nodejs-npm
#RUN apk update && apk add nodejs nodejs-npm && npm i -g nodemon

# Expose any ports we need open (do this later as required)
#EXPOSE 80

# Define our command to be run when launching the container
CMD ["python", "virgin1bot.py"]
