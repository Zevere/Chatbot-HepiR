# Zevere Bot for Telegram

[![Docker Badge]](https://hub.docker.com/r/zevere/chatbot-hepir)

First time developing a telegram bot

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/0571788a6ff2473081bab5d72e4c1172)](https://www.codacy.com/app/Zevere/Chatbot-HepiR?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Zevere/Chatbot-HepiR&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/Zevere/Chatbot-HepiR.svg?branch=master)](https://travis-ci.org/Zevere/Chatbot-HepiR)
## to build image

```sh
cd scripts && npm i && cd .. && node scripts/build
```

## to run the image to start up the bot

```sh
docker run -it \
	-e MONGODB_URI=<URI>	\
	-e TOKEN=<BOT_TOKEN> \
	-e PORT=<port for flask app to run on> \
	-e BOT_USERNAME=<BOT_USERNAME>	\
	-e VIVID_USER=<VIVID_USER>	\
	-e VIVID_PASSWORD=<VIVID_PASSWORD>	\
	chatbot-hepir
```

## heroku cli commands used

```sh
heroku login
heroku create <app name>
git push heroku master
heroku ps:scale (web|worker)=(0|1)
heroku logs --tail
```

## credits
https://github.com/eternnoir/pyTelegramBotAPI

[Docker Badge]: https://img.shields.io/docker/pulls/zevere/chatbot-hepir.svg
