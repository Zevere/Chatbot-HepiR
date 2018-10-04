import json
import os

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import InlineQueryHandler

from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent

VERSION="2.0.0"
UNDERSTANDABLE_LANGUAGE=('hello','bonjour','hi','greetings','sup')
KNOWN_COMMANDS=('start','about','caps')

def start(bot,update):
    print(update)
    print('Received /start command from user: {}'.format(update.message.chat.first_name))
    bot.send_message(chat_id=update.message.chat_id,text="I'm the HepiR bot, please talk to me!\n\nType /about to learn more about me :)!")

def about(bot,update):
    print('Received /about command from user: {}'.format(update.message.chat.first_name))
    bot.send_message(chat_id=update.message.chat_id,text="HepiR - v{}\nLately, I've been, I've been thinking\nI want you to be happier, I want you to use Zevere!\n\nI understand the follow commands:\n{}".format(VERSION,KNOWN_COMMANDS))

def echo(bot,update):
    print('Received regular message: {} from user: {}'.format(update.message.text,update.message.chat.first_name))
    bot.send_message(chat_id=update.message.chat_id,text=update.message.text)

def caps(bot, update, args):
    print('Received /caps command from user: {}'.format(update.message.chat.first_name))
    text_caps=' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id,text=text_caps)

def inline_caps(bot,update):
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

def unknown_command(bot,update):
    print('Unknown command issued: {} by user: {}'.format(update.message.text,update.message.chat.first_name))
    bot.send_message(chat_id=update.message.chat_id,text="Sorry, I did not understand that command.")

def main():
    # read config from env file
    CONFIGS=os.environ['CONFIGS']
    api_token=json.loads(CONFIGS)['token']
    #api_token='651982727:AAGZHYc-nEOFDZefOXqIgoogZFZKNvJs6TY'
    updater=Updater(token=api_token)
    dispatcher=updater.dispatcher

    print("Starting bot now")

    start_handler=CommandHandler('start',start)
    dispatcher.add_handler(start_handler)

    echo_handler=MessageHandler(Filters.text,echo)
    dispatcher.add_handler(echo_handler)

    caps_handler=CommandHandler('caps',caps,pass_args=True)
    dispatcher.add_handler(caps_handler)

    inline_caps_handler=InlineQueryHandler(inline_caps)
    dispatcher.add_handler(inline_caps_handler)

    dispatcher.add_handler(CommandHandler('about',about))

    dispatcher.add_handler(MessageHandler(Filters.command,unknown_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
