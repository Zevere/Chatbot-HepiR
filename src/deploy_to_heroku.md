# Deploy to Heroku
Have these files in root of folder
- webhook_flask_tgbot.py
- requirements.txt
- Procfile

## Procfile contents
`web: python3 <app file name>.py`

## Heroku CLI commands
1. `git init`
2. `heroku login`
3. `heroku create --region us chatbot-hepir`
4. `heroku buildpacks:set heroku/python`
5. `git push heroku master`
6. `heroku config:set TOKEN=<BOT TOKEN>`
7. `heroku ps:scale web=1`
8. `heroku logs --tail`

To turn off bot
1. `heroku ps:stop web`