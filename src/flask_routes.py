from pprint import pprint
import datetime
import requests
from flask import request, redirect
from properties import *
from helper_methods import connect


# webhook will send update to the bot, so need to process update messages received
@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "", 200


@app.route('/', methods=['GET'])
def index():
    return "Come check me out at {}/{}!".format(TG_USERNAME_URL, BOT_USERNAME), 200


# WEBHOOK_URL/api/login-widget?zv-user=ZV_USER&id=TELEGRAM_USERID&first_name=TELEGRAM_FIRST_NAME&auth_date=CURR_EPOCH_TIME&hash=HASH
@app.route('/api/login-widget', methods=['GET'])
def login_widget():
    first_name = request.args.get('first_name')
    tg_id = str(request.args.get('id'))
    zv_user = request.args.get('zv-user')
    connect(zv_user, tg_id, first_name=first_name)
    return redirect('{}/{}'.format(TG_USERNAME_URL, BOT_USERNAME))


@app.route('/getWebhookInfo')
def get_webhook_info():
    return redirect('https://api.telegram.org/bot{}/getWebhookInfo'.format(TOKEN))
