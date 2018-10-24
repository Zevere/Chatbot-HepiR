import os

from flask import Flask, request

import telebot

TOKEN = os.environ['TOKEN']
WEBHOOK_URL = 'https://chatbot-hepir.herokuapp.com/'
PORT = int(os.environ.get('PORT', '8443'))
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

bot.remove_webhook()


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, 'Hello, ' + msg.from_user.first_name)


@bot.message_handler(func=lambda msg: True, content_types=['text'])
def echo_message(msg):
    bot.reply_to(msg, msg.text)


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "!", 200


@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    return "!", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
