import json
import os
import requests

from pprint import pprint

from telegram.ext import (
        Updater,
        CommandHandler,
        MessageHandler,
        Filters,
        InlineQueryHandler
        )

from telegram import (
        ReplyKeyboardMarkup,
        KeyboardButton,
        InlineQueryResultArticle,
        InputTextMessageContent
        )

from pymongo import MongoClient

# global vars
VERSION="2.1.3"
UNDERSTANDABLE_LANGUAGE=('hello','bonjour','hi','greetings','sup')
KNOWN_COMMANDS=('/start','/about','/caps <insert text>','/weather')

class HepiRBot:
    def __init__(self,owt):
        self.owt=owt

    def start(self,bot,update):
        print(update)
        print_transaction(update,'start')
        bot.send_message(chat_id=update.message.chat_id,text="I'm the HepiR bot, please talk to me!\n\nType /about to learn more about me :)!")

    def about(self,bot,update):
        print_transaction(update,'about')
        bot.send_message(chat_id=update.message.chat_id,text="HepiR - v{}\nLately, I've been, I've been thinking\nI want you to be happier, I want you to use Zevere!\n\nI understand the follow commands:\n{}\n\n...and I echo all regular messages you send to me so you will never be lonely ;).".format(VERSION,KNOWN_COMMANDS))

    def echo(self,bot,update):
        print_transaction(update,'',False)
        bot.send_message(chat_id=update.message.chat_id,text=update.message.text)

    def caps(self,bot, update, args):
        print_transaction(update,'caps')
        text_caps=' '.join(args).upper()
        bot.send_message(chat_id=update.message.chat_id,text=text_caps)

    def inline_caps(self,bot,update):
        query=update.inline_query.query
        if not query:
            return
        results=list()
        results.append(
                InlineQueryResultArticle(
                    id=query.upper(),
                    title='Caps',
                    input_message_content=InputTextMessageContent(query.upper())
                    )
                )
        bot.answer_inline_query(update.inline_query.id,results)

    def unknown_command(self,bot,update):
        print_transaction(update,'unknown_command')
        bot.send_message(chat_id=update.message.chat_id,text="Sorry, I did not understand that command.")

    def weather(self,bot,update):
        print_transaction(update,'weather')
        location_keyboard = KeyboardButton(text="send_location", request_location=True)
        custom_keyboard=[[ location_keyboard, 'Cancel' ]]
        reply_markup=ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)
        bot.send_message(chat_id=update.message.chat_id,
                text='Please share your location to determine the local weather.',
                reply_markup=reply_markup)

    def location(self,bot,update):
        fname=update.message.chat.first_name
        lon=update.message.location.longitude
        lat=update.message.location.latitude
        bot.send_message(chat_id=update.message.chat_id,text='Thank you {}.\nI now know you are located at latitude: {}, longitude: {}'.format(fname,lat,lon))
        local_weather=requests.get('https://api.openweathermap.org/data/2.5/weather?lon={}&lat={}&appid={}&units=metric'.format(lon,lat,self.owt)).json()
        bot.send_message(chat_id=update.message.chat_id,text='Your local weather is:\n\n{},{}\n{}\u00b0C\n{} with {}'.format(local_weather['name'],local_weather['sys']['country'],local_weather['main']['temp'],local_weather['weather'][0]['main'],local_weather['weather'][0]['description']))
        print(update.message.location)
        print('local weather: {}'.format(local_weather))

# helper functions
def print_transaction(update,cmd,is_command=True):
    if cmd is "unknown_command":
        print('Unknown command issued: "{}" by user: {}'.format(update.message.text,update.message.chat.first_name))
    elif is_command:
        print('Received "/{}" command from user: {}'.format(cmd,update.message.chat.first_name))
    else:
        print('Received regular message: "{}" from user: {}'.format(update.message.text,update.message.chat.first_name))

def main():
    # read config from env file
    CONFIGS=os.environ['CONFIGS']
    bot_token=json.loads(CONFIGS)['bot_token']
    openweather_token=json.loads(CONFIGS)['openweather_token']
    updater=Updater(token=bot_token)
    dispatcher=updater.dispatcher

    hepirbot=HepiRBot(openweather_token)

    # opening mlab mongodb connection
    mongodb_uri='mongodb://kbmakevin:fastpath6479@ds227853.mlab.com:27853/'
    mongodb_dbname='hepir'
    client = MongoClient(mongodb_uri)
    db = client[mongodb_dbname]

    print("Starting HepiR bot now...")
    pprint(db)

    dispatcher.add_handler(CommandHandler('start',hepirbot.start))
    dispatcher.add_handler(MessageHandler(Filters.text,hepirbot.echo))
    dispatcher.add_handler(CommandHandler('caps',hepirbot.caps,pass_args=True))
    dispatcher.add_handler(InlineQueryHandler(hepirbot.inline_caps))
    dispatcher.add_handler(CommandHandler('about',hepirbot.about))
    dispatcher.add_handler(CommandHandler('weather',hepirbot.weather))
    dispatcher.add_handler(MessageHandler(Filters.location,hepirbot.location))
    dispatcher.add_handler(MessageHandler(Filters.command,hepirbot.unknown_command))

    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
