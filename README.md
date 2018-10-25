# Zevere Bot for Telegram

[![Docker Badge]](https://hub.docker.com/r/zevere/chatbot-hepir)

First time developing a telegram bot

## to build image

```sh
cd scripts && npm i && cd .. && node scripts/build
```

## to run the image to start up the bot

```sh
docker run -it -e TOKEN=<BOT_TOKEN> -e OPENWEATHER_TOKEN=<OpenWeather TOKEN> -e PORT=<port for flask app to run on> chatbot-hepir
```

## heroku cli commands used

```sh
heroku login
heroku create <app name>
git push heroku master
heroku ps:scale (web|worker)=(0|1)
heroku logs
```

## credits
https://github.com/eternnoir/pyTelegramBotAPI

[Docker Badge]: https://img.shields.io/docker/pulls/zevere/chatbot-hepir.svg
