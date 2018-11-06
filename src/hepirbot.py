import os
import requests
import datetime
import telebot
from flask import Flask, request, redirect
from pymongo import MongoClient
from pprint import pprint

# VARS ----------------------------------------------------------------------------------------------------
VERSION = "3.4.5"
UNDERSTANDABLE_LANGUAGE = ('hello', 'bonjour', 'hi', 'greetings', 'sup')
KNOWN_COMMANDS = ('/start', '/about', '/login', '/me', '/caps <insert text>')

LOCAL_ENV = False

if LOCAL_ENV:
    from src.dev_env import *
else:
    WEBHOOK_URL = 'https://zv-s-chatbot-hepir.herokuapp.com/'

    # picked up from heroku configs
    PORT = int(os.environ['PORT'])
    TOKEN = os.environ['TOKEN']
    MONGODB_URI = os.environ['MONGODB_URI']
    BOT_USERNAME = os.environ['BOT_USERNAME']
    VIVID_USER = os.environ['VIVID_USER']
    VIVID_PASSWORD = os.environ['VIVID_PASSWORD']

# hardcoded constants because we decided not to use heroku environment variables for these things
MONGODB_COLLECTION = 'users'
# last element at end of URI
MONGODB_DBNAME = MONGODB_URI.split('/')[-1]

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
    tg_id = str(request.args.get('id'))
    zv_user = request.args.get('zv-user')
    widget_hash = request.args.get('hash')

    # TODO: telegram chat bot web app verifies that the authorization is sent by Telegram and not some third party

    # check if zv_user already exists; duplicate users results in 503 error from VIVID API
    should_connect_hepir = False
    vivid_request = requests.get('https://zv-s-botops-vivid.herokuapp.com/api/v1/user-registrations/{}'.format(zv_user),
                                 auth=(VIVID_USER, VIVID_PASSWORD))

    print(
        '[{}] The status code of the vivid_request ([{}]: {}) is: {}'.format(str(datetime.datetime.now()).split('.')[0],
                                                                             vivid_request.request,
                                                                             vivid_request.url,
                                                                             vivid_request.status_code))

    # status_code == 200
    # USE CASE 1: zv_user registered in Zevere and connected with Calista but NOT HepiR
    if vivid_request.status_code == 200:
        print('[{}] User registration found for ({})'.format(str(datetime.datetime.now()).split('.')[0], zv_user))
        pprint(vivid_request.json())
        should_connect_hepir = True

    # status_code == 400
    # USE CASE 2: zv_user is not registered in Zevere
    elif vivid_request.status_code == 400:
        print('[{}] User ID ({}) is invalid or does not exist'.format(str(datetime.datetime.now()).split('.')[0],
                                                                      zv_user))
        pprint(vivid_request.json())
        # should never get here because can only access Login Widget workflow on Profile page after logging in via Coherent

    # status_code == 404
    # USE CASE 3: zv_user is registered but not connected to Calista or HepiR
    elif vivid_request.status_code == 404:
        print('[{}] User ({}) has not registered with any of the Zevere chat bots'.format(
            str(datetime.datetime.now()).split('.')[0], zv_user))
        pprint(vivid_request.json())
        should_connect_hepir = True

    # connect zv_user to tg_id if not exists in hepir db
    # send post with {
    #   "username": "string",
    #   "chatUserId": "string"
    # }
    # as payload to vivid api
    if should_connect_hepir:
        # if user connection already in hepir db, don't add again
        if user_collection.find_one({
            'zv_user': zv_user,
            'tg_id': tg_id
        }):
            print('[{}] (zv_user={}, tg_id={}) found in (db={}) => {} is a returning user :)!'.format(
                str(datetime.datetime.now()).split('.')[0], zv_user, tg_id, MONGODB_DBNAME, first_name))
            print('[{}] will not be adding (zv_user={}, tg_id={}) to (db={})'.format(
                str(datetime.datetime.now()).split('.')[0], zv_user,
                tg_id, MONGODB_DBNAME))

            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=You are already logged in to Zevere with the id of `{}`!parse_mode=Markdown'.format(
                    TOKEN, tg_id, zv_user))

        # if zv_user connected to another tg_id, don't connect
        elif user_collection.find_one({
            'zv_user': zv_user
        }):
            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Zevere User ID `{}` is already connected to antoher telegram account!parse_mode=Markdown'.format(
                    TOKEN, tg_id, zv_user))

        # if tg_id connected to another zv_user, don't connect
        elif user_collection.find_one({
            'tg_id': tg_id
        }):
            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Your telegram account is already connected to another Zevere ID!parse_mode=Markdown'.format(
                    TOKEN, tg_id))

        # zv user - tg user connection not found in hepir db => add connection to hepir db
        else:
            print(
                '[{}] No users found matching (zv_user={}, tg_id={}) in (db={})'.format(
                    str(datetime.datetime.now()).split('.')[0],
                    zv_user, tg_id, MONGODB_DBNAME))
            print('[{}] adding (zv_user={}, tg_id={}) to (db={})...'.format(str(datetime.datetime.now()).split('.')[0],
                                                                            zv_user, tg_id, MONGODB_DBNAME))
            new_user_id = user_collection.insert_one({
                'zv_user': zv_user,
                'tg_id': tg_id
            }).inserted_id
            print('[{}] new user (zv_user={}, tg_id={}) inserted into (db={}): (inserted_id={})'.format(
                str(datetime.datetime.now()).split('.')[0], zv_user, tg_id, MONGODB_DBNAME,
                new_user_id))

            # send post request to vivid api with payload containing zv user and tg user id
            vivid_request = requests.post('https://zv-s-botops-vivid.herokuapp.com/api/v1/user-registrations',
                                          json={"username": zv_user, "chatUserId": tg_id},
                                          auth=(VIVID_USER, VIVID_PASSWORD))

            print('vivid_request is: {}'.format(vivid_request))
            print('[{}] The status code of the vivid_request ([{}]: {}) is: {}'.format(
                str(datetime.datetime.now()).split('.')[0],
                vivid_request.request,
                vivid_request.url,
                vivid_request.status_code))
            print('[{}] The json of the vivid_request ([{}]: {}) is: {}'.format(
                str(datetime.datetime.now()).split('.')[0],
                vivid_request.request,
                vivid_request.url,
                vivid_request.json()))

            if vivid_request.status_code == 201:
                print(
                    '[{}] Zevere User (zv_user={}) has been succesfully connected to telegram account (tg_id={})'.format(
                        str(datetime.datetime.now()).split('.')[0], zv_user, tg_id))
                requests.get(
                    'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=You have successfully connected your telegram account to the Zevere ID: `{}`!parse_mode=Markdown'.format(
                        TOKEN, tg_id, zv_user))

            elif vivid_request.status_code == 400:
                print(
                    '[{}] There are invalid fields in the POST request to VIVID API or the username (zv_user={}) does not exist on Zevere'.format(
                        str(datetime.datetime.now()).split('.')[0], zv_user))
                requests.get(
                    'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Unable to connect your telegram account to the Zevere ID: `{}` due to internal server errors!parse_mode=Markdown'.format(
                        TOKEN, tg_id, zv_user))

    else:
        # sends feedback to user confirming login
        requests.get(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Zevere User ID `{}` is invalid or does not exist!&parse_mode=Markdown'.format(
                TOKEN, tg_id, zv_user))

    return redirect('https://t.me/{}'.format(BOT_USERNAME))


@app.route('/getWebhookInfo')
def get_webhook_info():
    return redirect('https://api.telegram.org/bot{}/getWebhookInfo'.format(TOKEN))


# Telegram Bot Command Handlers --------------------------------------------------------------------------
@bot.message_handler(commands=['me'])
def get_profile(msg):
    log_command_info('/me', msg)

    # my tg id
    tg_id = msg.chat.id

    # get zv_user of the connected account from the hepir db
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})

    if found_connection:
        zv_user = found_connection.get('zv_user')

        # query vivid to get zevere profile associated with connected zv_user
        #     e.g. GET https://zv-s-botops-vivid.herokuapp.com/api/v1/operations/getUserProfile/?username=kevin.ma
        vivid_request = requests.get(
            'https://zv-s-botops-vivid.herokuapp.com/api/v1/operations/getUserProfile/', params={'username': zv_user},
            auth=(VIVID_USER, VIVID_PASSWORD))

        resp = vivid_request.json()

        fname = resp.get('firstName')
        zv_user = resp.get('id')
        joined_at = resp.get('joinedAt')
        lname = resp.get('lastName')

        print('found this resp:')
        pprint(resp)

        # bot.send_message(msg.chat.id,
        #                  'You are logged into Zevere as `{}`\n---\nProfile\n---\nZevere Id: `{}`\nFirst Name: {}\nLast Name: {}\n Joined At: {}'.format(
        #                      zv_user, zv_user, fname, lname, joined_at), parse_mode="Markdown")

        bot.send_message(msg.chat.id,
                         'You are logged in as *{} {}* (`{}`).'.format(fname, lname, zv_user), parse_mode="Markdown")

    # zv user - tg user connection not found in hepir db => add connection to hepir db
    else:
        print(
            '[{}] No connections found matching (tg_id={}) in (db={})'.format(
                str(datetime.datetime.now()).split('.')[0], tg_id, MONGODB_DBNAME))

        bot.send_message(msg.chat.id,
                         'You are not logged into Zevere. Please login at https://zv-s-webapp-coherent.herokuapp.com/ and use the Login Widget provided on the Profile page after logging in :)!')


# If logged in, HepiR sends friendly welcome message and tells tg user who they are logged in as (zv_user)
# Else, provides redirect link to user to login to Coherent and tells them to click on login widget under profile
@bot.message_handler(commands=['login'])
def login(msg):
    log_command_info('/login', msg)

    # my tg id
    tg_id = msg.chat.id

    # get zv_user of the connected account from the hepir db
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})

    if found_connection:
        zv_user = found_connection.get('zv_user')

        # query vivid to get zevere profile associated with connected zv_user
        #     e.g. GET https://zv-s-botops-vivid.herokuapp.com/api/v1/operations/getUserProfile/?username=kevin.ma
        vivid_request = requests.get(
            'https://zv-s-botops-vivid.herokuapp.com/api/v1/operations/getUserProfile/', params={'username': zv_user},
            auth=(VIVID_USER, VIVID_PASSWORD))

        bot.send_message(msg.chat.id,
                         'You are  currently logged into Zevere as (`{}`)\nWelcome, {}. I hope you are Hepi ;)!'.format(
                             zv_user,
                             msg.from_user.first_name),
                         parse_mode="Markdown")

    # zv user - tg user connection not found in hepir db => add connection to hepir db
    else:
        print(
            '[{}] No connections found matching (tg_id={}) in (db={})'.format(
                str(datetime.datetime.now()).split('.')[0], tg_id, MONGODB_DBNAME))

        bot.send_message(msg.chat.id,
                         'You are not logged into Zevere. Please login at https://zv-s-webapp-coherent.herokuapp.com/ and use the Login Widget provided on the Profile page after logging in :)!')


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
                                                   telebot.types.InputTextMessageContent(
                                                       inline_query.query.upper()))
        log_inline_query_info(inline_query.query, inline_query)
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)


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
    print("[{}] Starting HepiR using (BOT_NAME={}) and (TOKEN={}) now...".format(
        str(datetime.datetime.now()).split('.')[0], BOT_USERNAME, TOKEN))
    bot.remove_webhook()
    if LOCAL_ENV:
        bot.polling(none_stop=True)
    else:
        bot.set_webhook(url=WEBHOOK_URL + TOKEN)


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
    app.run(host='0.0.0.0', port=PORT)
