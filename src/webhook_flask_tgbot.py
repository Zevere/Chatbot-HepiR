import logging
import time

import flask

import telebot

API_TOKEN = '752142027:AAGCp47hpBa3LYkBgEXMUlftOABpndyqwOM'

# ip/host where the bot is running
WEBHOOK_HOST = 'localhost'

# telegram bot only lets us use 8443, 443 80, or 88
WEBHOOK_PORT = 8443

# WEBHOOK_LISTEN = '0.0.0.0'
WEBHOOK_LISTEN = '0.0.0.0'

# path to ssl cert
WEBHOOK_SSL_CERT = './webhook_cert.pem'
# path to ssl private key
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'Successful Connection'


# start flask server
app.run(host=WEBHOOK_HOST,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
