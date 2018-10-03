from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent
from telegram.ext import InlineQueryHandler
import logging

updater=Updater(token='651982727:AAHHKgnPSMdOScxWTR5G7nSdsQELduQar1Y')
dispatcher=updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot,update):
    print(update)
    print('Received /start command from user: {}'.format(update.message.chat.first_name))
    bot.send_message(chat_id=update.message.chat_id,text="I'm a bot, please talk to me!")

def echo(bot,update):
    print('Received regular message: {} from user: {}'.format(update.message.text,update.message.chat.first_name))
    bot.send_message(chat_id=update.message.chat_id,text=update.message.text)

def caps(bot, update, args):
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

def unknown(bot,update):
    bot.send_message(chat_id=update.message.chat_id,text="Sorry, I did not understand that command.")

# we want the bot to say message every time a tg msg contains /start command
# we register the CommandHandler in the dispatcher
start_handler=CommandHandler('start',start)
dispatcher.add_handler(start_handler)

echo_handler=MessageHandler(Filters.text,echo)
dispatcher.add_handler(echo_handler)

caps_handler=CommandHandler('caps',caps,pass_args=True)
dispatcher.add_handler(caps_handler)

inline_caps_handler=InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

dispatcher.add_handler(MessageHandler(Filters.command,unknown))

updater.start_polling()
updater.idle()
