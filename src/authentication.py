import requests
from properties import *
from pprint import pprint
import datetime


def is_authenticated(tg_id):
    """Used to enforce authentication. Returns true if the current telegram user is connected to an existing Zevere account, false otherwise.
    """
    return get_authenticated_zvuser(tg_id) is not None


def get_authenticated_zvuser(tg_id):
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})
    print('get_authenticated_zvuser')
    print('\tfound_connection for tg_id={} is {}'.format(tg_id, found_connection))
    if found_connection:
        return found_connection.get('zv_user')
    return None


# optional params, will not be used in testing
def connect(zv_user, tg_id, first_name="He/She", bot=None, msg=None):
    # check if zv_user already exists; duplicate users results in 503 error from VIVID API
    should_add_connection_to_hepir_db = False
    vivid_request = requests.get('{}/api/v1/user-registrations/{}'.format(VIVID_ROOT_URL, zv_user),
                                 auth=(VIVID_USER, VIVID_PASSWORD))

    print(
        '[{}] The status code of the vivid_request ([{}]: {}) is: {}'.format(str(datetime.datetime.now()).split('.')[0],
                                                                             vivid_request.request,
                                                                             vivid_request.url,
                                                                             vivid_request.status_code))

    # status_code == 200
    # USE CASE 1: zv_user registered in Zevere and connected with Calista but NOT HepiR
    if vivid_request.status_code == 200:
        print('[{}] User registration found for ({})'.format(
            str(datetime.datetime.now()).split('.')[0], zv_user))
        pprint(vivid_request.json())
        should_add_connection_to_hepir_db = True

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
        should_add_connection_to_hepir_db = True

    # connect zv_user to tg_id if not exists in hepir db
    # send post with {
    #   "username": "string",
    #   "chatUserId": "string"
    # }
    # as payload to vivid api
    if should_add_connection_to_hepir_db:
        # if user connection already in hepir db, don't add again
        if user_collection.find_one({
            'zv_user': zv_user,
            'tg_id': str(tg_id)
        }):
            print('[{}] (zv_user={}, tg_id={}) found in (db={}) => {} is a returning user :)!'.format(
                str(datetime.datetime.now()).split('.')[0], zv_user, tg_id, MONGODB_DBNAME, first_name))
            print('[{}] will not be adding (zv_user={}, tg_id={}) to (db={})'.format(
                str(datetime.datetime.now()).split('.')[0], zv_user,
                tg_id, MONGODB_DBNAME))

            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=You are already logged into Zevere with the id of `{}`!&parse_mode=Markdown'.format(
                    TOKEN, tg_id, zv_user))

            return True, 'You are already logged into Zevere with the id of {}.'.format(zv_user)

        # if zv_user connected to another tg_id, don't connect
        elif user_collection.find_one({
            'zv_user': zv_user
        }):
            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Zevere User ID `{}` is already connected to another telegram account!&parse_mode=Markdown'.format(
                    TOKEN, tg_id, zv_user))

            return False, "{} is already connected to another telegram account!".format(zv_user)

        # if tg_id connected to another zv_user, don't connect
        elif user_collection.find_one({
            'tg_id': str(tg_id)
        }):
            requests.get(
                'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Your telegram account is already connected to another Zevere ID!&parse_mode=Markdown'.format(
                    TOKEN, tg_id))

            return False, "Your telegram account is already connected to another Zevere ID!"

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
                str(datetime.datetime.now()).split('.')[
                    0], zv_user, tg_id, MONGODB_DBNAME,
                new_user_id))

            # send post request to vivid api with payload containing zv user and tg user id
            vivid_request = requests.post('{}/api/v1/user-registrations'.format(VIVID_ROOT_URL),
                                          json={"username": zv_user,
                                                "chatUserId": tg_id},
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

                return True, 'You have successfully logged into the Zevere account {} with your telegram account of {}'.format(zv_user, tg_id)

            elif vivid_request.status_code == 400:
                print(
                    '[{}] There are invalid fields in the POST request to VIVID API or the username (zv_user={}) does not exist on Zevere'.format(
                        str(datetime.datetime.now()).split('.')[0], zv_user))

                # remove the entry we added to the hepir db, rollback transaction.
                user_collection.delete_one({
                    'zv_user': zv_user,
                    'tg_id': str(tg_id)
                })

                requests.get(
                    'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Unable to connect your telegram account to the Zevere ID: `{}` due to internal server errors!&parse_mode=Markdown'.format(
                        TOKEN, tg_id, zv_user))

                return False, 'You have provided invalid login credentials.'

    else:
        # sends feedback to user confirming login
        requests.get(
            'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Zevere User ID `{}` is invalid or does not exist!&parse_mode=Markdown'.format(
                TOKEN, tg_id, zv_user))

        return False, 'You have provided invalid login credentials.'

    return False, 'You have provided invalid login credentials.'


# optional params here, will not be used in testing
def disconnect(zv_user, tg_id, bot=None, msg=None):
    # send DELETE request to vivid to remove the  associations of an existing Zevere user to the Zevere chat bots.
    should_remove_connection_from_hepir_db = False
    vivid_request = requests.delete('{}/api/v1/user-registrations/{}'.format(VIVID_ROOT_URL, zv_user),
                                    auth=(VIVID_USER, VIVID_PASSWORD))

    print(
        '[{}] The status code of the vivid_request ([{}]: {}) is: {}'.format(str(datetime.datetime.now()).split('.')[0],
                                                                             vivid_request.request,
                                                                             vivid_request.url,
                                                                             vivid_request.status_code))
    # Reference from documentation provided at: https://zv-botops-vivid.herokuapp.com/api/docs/swagger/index.html

    # status_code == 204
    # Registration is deleted
    if vivid_request.status_code == 204:
        print('[{}] Registration is deleted for ({})'.format(
            str(datetime.datetime.now()).split('.')[0], zv_user))
        should_remove_connection_from_hepir_db = True

    # status_code == 400
    # User ID is invalid or does not exist
    elif vivid_request.status_code == 400:
        print('[{}] User ID ({}) is invalid or does not exist'.format(str(datetime.datetime.now()).split('.')[0],
                                                                      zv_user))
        pprint(vivid_request.json())

    # status_code == 404
    # User has not registered with any of the Zevere chat bots
    elif vivid_request.status_code == 404:
        print('[{}] User ({}) has not registered with any of the Zevere chat bots'.format(
            str(datetime.datetime.now()).split('.')[0], zv_user))
        pprint(vivid_request.json())

    if should_remove_connection_from_hepir_db:
        # remove user connection from hepir db, if it exists
        if user_collection.find_one({
            'zv_user': zv_user,
            'tg_id': str(tg_id)
        }):
            result = user_collection.delete_one({
                'zv_user': zv_user,
                'tg_id': str(tg_id)
            }).deleted_count

            if result == 1:
                print('[{}] Successfully removed {} user with zv_user={} and tg_id={} from the HepiR database.'.format(
                    str(datetime.datetime.now()).split('.')[0], result, zv_user, tg_id))

                if bot is not None:
                    bot.send_message(msg.chat.id, 'You have successfully disconnected your telegram account from the Zevere ID: `{}`'.format(zv_user),
                                     parse_mode="Markdown"
                                     )
                return True, 'You have successfully been logged out from {}'.format(zv_user)

            else:
                print('[{}] Failed to remove user with zv_user={} and tg_id={} from the HepiR database.'.format(
                    str(datetime.datetime.now()).split('.')[0], zv_user, tg_id))
                return False, 'You have failed to log out from {}'.format(zv_user)

        # if user connection does not exist in hepir db, don't need to remove
        else:
            if bot is not None:
                bot.send_message(msg.chat.id, 'Your telegram account is not connected to the Zevere ID: `{}`'.format(zv_user),
                                 parse_mode="Markdown"
                                 )
            return False, 'You are not logged in to any Zevere account.'

    return False, 'You are not logged in to any Zevere account.'
