# virgin1bot
First time developing a telegram bot

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
