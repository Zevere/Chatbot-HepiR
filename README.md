# virgin1bot

First time developing a telegram bot

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/0571788a6ff2473081bab5d72e4c1172)](https://www.codacy.com/app/Zevere/Chatbot-HepiR?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Zevere/Chatbot-HepiR&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.org/Zevere/Chatbot-HepiR.svg?branch=master)](https://travis-ci.org/Zevere/Chatbot-HepiR)
## to build image
```
cd scripts
npm i
cd ..
node scripts/build
```

## to run the image to start up the bot
```
docker run --rm --env CONFIGS='{"token":"TOKEN"}' chatbot-kev
```

## heroku cli commands used
```
heroku login
heroku create <app name>
git push heroku master
heroku ps:scale (web|worker)=(0|1)
heroku logs
```
