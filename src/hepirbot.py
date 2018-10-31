import os
import requests
import datetime
import telebot
from flask import Flask, request, redirect
from pymongo import MongoClient
from pprint import pprint

# VARS ----------------------------------------------------------------------------------------------------
VERSION = "3.0.0"
UNDERSTANDABLE_LANGUAGE = ('hello', 'bonjour', 'hi', 'greetings', 'sup')
KNOWN_COMMANDS = ('/start', '/about', '/caps <insert text>', '/weather')

WEBHOOK_URL = 'https://zv-s-chatbot-hepir.herokuapp.com/'

# picked up from heroku configs
TOKEN = os.environ['TOKEN']
PORT = int(os.environ['PORT'])
OPENWEATHER_TOKEN = os.environ['OPENWEATHER_TOKEN']
MONGODB_URI = os.environ['MONGODB_URI']
MONGODB_DBNAME = os.environ['MONGODB_DBNAME']
MONGODB_COLLECTION = os.environ['MONGODB_COLLECTION']
BOT_USERNAME = os.environ['BOT_USERNAME']

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DBNAME]
user_collection = db[MONGODB_COLLECTION]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# Flask Routes ------------------------------------------------------------------------------------------
# webhook will send update to the bot, so need to process update messages received
@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return "", 200


@app.route('/', methods=['GET'])
def index():
    return "Come check me out at https://t.me/ZevereBot!", 200


# https://zv-s-chatbot-hepir.herokuapp.com/api/login-widget?zv-user=ZV_USER&id=TELEGRAM_USERID&first_name=TELEGRAM_FIRST_NAME&auth_date=CURR_EPOCH_TIME&hash=HASH
@app.route('/api/login-widget', methods=['GET'])
def login_widget():
    auth_date = request.args.get('auth_date')
    first_name = request.args.get('first_name')
    tg_id = request.args.get('id')
    zv_user = request.args.get('zv-user')
    widget_hash = request.args.get('hash')

    # TODO: telegram chat bot web app verifies that the authorization is sent by Telegram and not some third party

    # if telegram userid does not exist, stores the telegram userid, and user's name in telegram chat bot database
    if user_collection.find_one({
        'zv_user': zv_user,
        'tg_id': tg_id
    }):
        print('[{}] tg_id {} found in the database...{} is a returning user :)!'.format(
            str(datetime.datetime.now()).split('.')[0], tg_id, first_name))
        print('[{}] will not be adding tg_id {} to db'.format(str(datetime.datetime.now()).split('.')[0], tg_id))
    else:
        print('[{}] No users found matching'.format(str(datetime.datetime.now()).split('.')[0]))
        print('[{}] adding tg_id {} to db...'.format(str(datetime.datetime.now()).split('.')[0], tg_id))
        new_user_id = user_collection.insert_one({
            'zv_user': zv_user,
            'tg_id': tg_id
        }).inserted_id
        print('[{}] new user inserted into db: {}'.format(str(datetime.datetime.now()).split('.')[0], new_user_id))

    # TODO: Telegram Chat Bot Web App sends POST request with username: ZV_USER and chatUserId: TELEGRAM_USER_ID to https://zv-s-botops-vivid.herokuapp.com/api/v1/user-registrations

    # sends feedback to user confirming login
    requests.get(
        'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=You have been logged into Zevere via the Login Widget :)!'.format(
            TOKEN, tg_id))

    return redirect('https://t.me/{}'.format(BOT_USERNAME))


@app.route('/getWebhookInfo')
def get_webhook_info():
    return redirect('https://api.telegram.org/bot{}/getWebhookInfo'.format(TOKEN))


# Telegram Bot Command Handlers --------------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    log_command_info('/start', msg)
    bot.send_message(msg.chat.id,
                     "Hello, {}. I'm the HepiR bot, please talk to me!\n\nType /about to learn more about me :)!".format(
                         msg.from_user.first_name))


@bot.message_handler(commands=['about'])
def about(msg):
    log_command_info('/about', msg)
    bot.send_message(msg.chat.id,
                     "HepiR - v{}\nLately, I've been, I've been thinking\nI want you to be happier, I want you to use Zevere!\n\nI understand the follow commands:\n{}\n\n...and I echo all regular messages you send to me so you will never be lonely ;).".format(
                         VERSION, KNOWN_COMMANDS))
    return


@bot.message_handler(commands=['caps'])
def caps(msg):
    log_command_info(msg.text, msg)
    args = extract_args(msg.text)
    if len(args) > 0:
        bot.reply_to(msg, "".join(map(lambda str: str.upper() + ' ', args)))
    else:
        return


@bot.inline_handler(lambda query: query)
def query_text(inline_query):
    try:
        r = telebot.types.InlineQueryResultArticle('1', 'Capitalize Message',
                                                   telebot.types.InputTextMessageContent(inline_query.query.upper()))
        log_inline_query_info(inline_query.query, inline_query)
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)


@bot.message_handler(commands=['weather'])
def weather(msg):
    log_command_info(msg.text, msg)
    location_keyboard = telebot.types.KeyboardButton(text='Send Location', request_location=True)

    reply_markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reply_markup.add(location_keyboard, 'Cancel')

    bot.send_message(msg.chat.id, text='Please share your location to determine the local weather :).',
                     reply_markup=reply_markup)
    return


@bot.message_handler(content_types=['location'])
def process_location(msg):
    log_received_text_msg(msg.location, msg)
    fname = msg.chat.first_name
    lon = msg.location.longitude
    lat = msg.location.latitude
    bot.send_message(msg.chat.id,
                     'Thank you {}.\nI now know you are located at latitude: {}, longitude: {}'.format(fname, lat, lon))
    local_weather = requests.get(
        'https://api.openweathermap.org/data/2.5/weather?lon={}&lat={}&appid={}&units=metric'.format(lon, lat,
                                                                                                     OPENWEATHER_TOKEN)).json()
    print('local weather: {}'.format(local_weather))

    bot.send_message(msg.chat.id, 'Your local weather is:\n\n{},{}\n{}\u00b0C\n{} with {}'.format(local_weather['name'],
                                                                                                  local_weather['sys'][
                                                                                                      'country'],
                                                                                                  local_weather['main'][
                                                                                                      'temp'],
                                                                                                  local_weather[
                                                                                                      'weather'][0][
                                                                                                      'main'],
                                                                                                  local_weather[
                                                                                                      'weather'][0][
                                                                                                      'description']))
    return


@bot.message_handler(content_types=['text'])
def echo_message(msg):
    log_received_text_msg(msg.text, msg)
    # first char, text starts with /, unknown command
    if msg.text[0] == '/':
        bot.reply_to(msg, 'Sorry, I did not understand the command: {}'.format(msg.text))
    else:
        bot.reply_to(msg, msg.text)


# Helper methods ------------------------------------------------------------------------------------------
# e.g. /caps what up dawg?! -> ['what', 'up', 'dawg?!']
def extract_args(msg):
    return msg.split()[1:]


# setup webhook and any other initialization processes
def init():
    print("Starting HepiR bot now...")
    bot.remove_webhook()
    # bot.polling(none_stop=True)
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    # return "Set Webhook to: {}".format(WEBHOOK_URL + TOKEN), 200


def log_command_info(cmd, msg):
    print(
        "[{}] Received '{}' command from '{}' (ID={})".format(str(datetime.datetime.now()).split('.')[0],
                                                              cmd,
                                                              (str(msg.from_user.first_name) + " " + str(
                                                                  msg.from_user.last_name)) if msg.from_user.last_name is not None else msg.from_user.first_name,
                                                              msg.from_user.id))
    return


def log_inline_query_info(query, msg):
    print(
        "[{}] Received inline query: '{}' from '{}' (ID={})".format(
            str(datetime.datetime.now()).split('.')[0], query,
            (str(msg.from_user.first_name) + " " + str(
                msg.from_user.last_name)) if msg.from_user.last_name is not None else msg.from_user.first_name,
            msg.from_user.id))
    return


def log_received_text_msg(txt, msg):
    print(
        "[{}] Received text: '{}' from '{}' (ID={})".format(str(datetime.datetime.now()).split('.')[0], txt,
                                                            (str(msg.from_user.first_name) + " " + str(
                                                                msg.from_user.last_name)) if msg.from_user.last_name is not None else msg.from_user.first_name,
                                                            msg.from_user.id))
    return


if __name__ == "__main__":
    init()
    # app.run(host='localhost', port=PORT)
    app.run(host='0.0.0.0', port=PORT)
