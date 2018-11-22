from pprint import pprint
import datetime
import requests
from flask import request, redirect
from . properties import *


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
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=You are already logged in to Zevere with the id of `{}`!&parse_mode=Markdown'.format(
                    TOKEN, tg_id, zv_user))

        # if zv_user connected to another tg_id, don't connect
        elif user_collection.find_one({
            'zv_user': zv_user
        }):
            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Zevere User ID `{}` is already connected to antoher telegram account!&parse_mode=Markdown'.format(
                    TOKEN, tg_id, zv_user))

        # if tg_id connected to another zv_user, don't connect
        elif user_collection.find_one({
            'tg_id': tg_id
        }):
            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Your telegram account is already connected to another Zevere ID!&parse_mode=Markdown'.format(
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
                    'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=You have successfully connected your telegram account to the Zevere ID: `{}`!&parse_mode=Markdown'.format(
                        TOKEN, tg_id, zv_user))

            elif vivid_request.status_code == 400:
                print(
                    '[{}] There are invalid fields in the POST request to VIVID API or the username (zv_user={}) does not exist on Zevere'.format(
                        str(datetime.datetime.now()).split('.')[0], zv_user))
                requests.get(
                    'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Unable to connect your telegram account to the Zevere ID: `{}` due to internal server errors!&parse_mode=Markdown'.format(
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
