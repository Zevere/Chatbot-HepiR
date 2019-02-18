# Zevere Bot for Telegram
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors)

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

## Contributors

Thanks goes to these wonderful people ([emoji key](https://github.com/all-contributors/all-contributors#emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
| [<img src="https://avatars2.githubusercontent.com/u/14854884?v=4" width="100px;" alt="Kevin Ma"/><br /><sub><b>Kevin Ma</b></sub>](https://github.com/kbmakevin)<br />[⚠️](https://github.com/Zevere/Chatbot-HepiR/commits?author=kbmakevin "Tests") [💻](https://github.com/Zevere/Chatbot-HepiR/commits?author=kbmakevin "Code") |
| :---: |
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!