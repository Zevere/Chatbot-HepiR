import requests
from properties import *
import datetime
from markup import *
from pprint import pprint


def is_authenticated(zv_user, tg_id):
    # TODO
    pass


def get_list_by_id(list_id):
    # TODO implement this func when the feature has been implemented in the BORZOO graphql api
    pass


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


def remove_reply_keyboard(tbot, cb_call):
    tbot.edit_message_reply_markup(
        chat_id=cb_call.message.chat.id, message_id=cb_call.message.json['message_id'], reply_markup=hide_inline_keyboard_markup())


def create_list(zv_user, list_title, list_description):
    """Creates a list for this Zevere user.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    list_title - the title of the list to be deleted
    list_description - Optional; the description of the list to be deleted

    Returns:
        True, list id   - upon successful creation
        False, None     - upon failure
    """

    list_id = convert_list_title_to_id(list_title)

    print(
        '\nLIST DETAILS\nlist_title={}\nlist_id={}\nlist_description={}\nowner={}\n'.format(
            list_title, list_id, list_description, zv_user)
    )

    # TODO change to use get list here instead of get_all_lists once the func is implemented in BORZOO

    # check if list exists for the user already
    owned_lists = get_all_lists(zv_user)
    for list in owned_lists:
        if list['id'] == list_id:
            return False, None

    # if reached here, means list does not already exist for this zv_user
    # send POST request to borzoo graphql web api to create list with the above list details
    if list_description is not None:
        response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                                 json={
            "query": "mutation {createList(owner: \"" + zv_user + "\", list: {id: \""+list_id+"\", title: \""+list_title+"\", description: \""+list_description+"\"}){id}}"
        },
            headers={'Content-Type': 'application/json'})
    else:
        response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                                 json={
            "query": "mutation {createList(owner: \"" + zv_user + "\", list: {id: \""+list_id+"\", title: \""+list_title+"\"}){id}}"
        },
            headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\ncreate_list\nresponse: {}\n'.format(response))
        return True, response['data']['createList']['id']
    else:
        # borzoo is offline
        return False, None

    return False, None

# need to use this when creating tasks/lists and verify that the id converted from the title will be within the 55 char limit boundary.


def is_valid_id_len(id):
    """Validates whether passed in id is within 55 character limit boundary.

    Due to telegram bot API restrictions, callback data can at most contain 64 characters. The callback headers in this app have been defined to be 9 chars in length. This leaves 55 char maximum for the variable data length.

    Returns:
        True, remaining characters left over from 55 - id length
        False, None
    """
    within_bounds = len(id) <= 55
    leftover_char_limit = 55-len(id)
    return within_bounds, leftover_char_limit


def convert_list_title_to_id(list_title):
    return list_title.strip().lower().replace(' ', '_')


def handle_create_list_description_force_reply(msg, list_title):
    list_description = msg.text

    if list_description == 'no':
        list_description = None

    zv_user = find_connected_zv_user(msg)

    # if list_description is not None:
    create_list_results = create_list(zv_user, list_title, list_description)
    # else:
    # create_list_results = create_list(zv_user, list_title)

    if create_list_results[0]:
        bot.send_message(msg.chat.id,
                         'Thank you for your input dear.\n\nYour new list has been successfully created with the following details:\n\nList Title: _{}_\nList Owner: _{}_{}'.format(
                             list_title, zv_user,
                             '\nList Description: _{}_'.format(
                                 list_description) if list_description is not None else ''
                         ),
                         parse_mode="Markdown"
                         )
    else:
        bot.send_message(msg.chat.id,
                         'An error has occured and the list was not created.',
                         parse_mode="Markdown",)

    return


def handle_create_list_id_force_reply(msg):
    """Solicits list title from user, then prompts user for list creation confirmation.
    """
    list_title = msg.text
    list_id = convert_list_title_to_id(list_title)
    print('\nlist_title={}\nlist_id={}'.format(list_title, list_id))
    print('len of the list_id={}\nValid len id={}\n'.format(
        len(list_id), is_valid_id_len(list_id)[0]))

    within_bounds, leftover_char_limit = is_valid_id_len(list_id)

    if within_bounds:
        # check that the list does not already exist in Zevere for this user
        zv_user = find_connected_zv_user(msg)
        owned_lists = get_all_lists(zv_user)
        for list in owned_lists:
            if list['id'] == list_id:
                bot.send_message(msg.chat.id, 'You already have a list created with the title of _{}_!\n\nYou cannot create duplicate lists with the same title in Zevere.\n\nPlease try again with a different name :)!'.format(
                    list_title),
                    parse_mode="Markdown"
                )
                return

        bot.send_message(msg.chat.id,
                         'Are you sure you want to `create` this list?\n\nYour new list will have a title of _{}_'.format(
                             list_title),
                         parse_mode="Markdown",
                         reply_markup=confirm_create_list_markup(list_title)
                         )
    else:
        bot.send_message(msg.chat.id,
                         'Your title is too long!The maximum number of characters permitted for a list title is 55 characters.\n\nYour list title exceeded this amount by *{}* characters.\n\nPlease return to List Management (/lists) and try again with a different title :)'.format(
                             abs(leftover_char_limit)),
                         parse_mode="Markdown"
                         )
    return


def delete_list(zv_user, list_id):
    """Deletes a list belonging to a Zevere user.

    Keyword arguments:
    zv_user - the user id of the Zevere user
    list_id - the id of the list to be deleted

    Returns:
        True, list id   - upon successful delete
        False, None     - if list does not exist for this Zevere user
    """
    # send POST request to borzoo graphql web api to delete list belonging to the current connected zv user
    response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                             json={
        "query": "mutation{ deleteList(owner:\"" + zv_user + "\", list:\""+list_id+"\")}"
    },
        headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\ndelete_list\nresponse: {}\n'.format(response))
        if response['data']['deleteList'] == True:
            return True, list_id
        else:
            # Task list not found
            return False, None
    else:
        # borzoo is offline
        return False, None


def delete_list_confirm_btn_clicked(msg, list_id):
    print('\n\nTrying to delete list with id = {}\n'.format(list_id))
    zv_user = find_connected_zv_user(msg)
    delete_list_results = delete_list(zv_user, list_id)

    if(delete_list_results[0]):
        bot.send_message(msg.chat.id,
                         'The list with the id `{}` was successfully deleted.'.format(
                             delete_list_results[1]),
                         parse_mode="Markdown",)
    else:
        bot.send_message(msg.chat.id,
                         'An error has occured and the list was not deleted.',
                         parse_mode="Markdown",)


def find_connected_zv_user(msg):
    """Gets the zevere user account connected to this telegram user.

    Keyword arguments:
    msg - the telegram message that intiated this function call

    Returns:
        Username of the Zevere account if found a connection with the current telegram account. Otherwise, returns None.
    """
    tg_id = msg.chat.id
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})
    if found_connection:
        return found_connection.get('zv_user')
    else:
        return None


def get_all_lists(zv_user):
    """Returns a list of all the lists owned by zv_user.

    Keyword arguments:
    zv_user -- the user id of the Zevere user
    """
    # send POST request to borzoo graphql web api to query lists belonging to connected zv user
    response = requests.post('{}/zv/graphql'.format(BORZOO_ROOT_URL),
                             json={
        "query": "query{ user(userId:\"" + zv_user + "\") { lists { id collaborators createdAt description owner tags tasks { id } title updatedAt } } }"
    },
        headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('\nget_all_lists\nresponse: {}\n'.format(response))
        if response['data']['user'] == None:
            owned_lists = None
        else:
            owned_lists = response['data']['user']['lists']
    else:
        owned_lists = None

    return owned_lists


def show_lists_to_delete(msg):
    zv_user = find_connected_zv_user(msg)
    owned_lists = get_all_lists(zv_user)
    if len(owned_lists) > 0:
        bot.send_message(msg.chat.id,
                         'Please click on the list you wish to `delete`:',
                         parse_mode="Markdown",
                         reply_markup=delete_list_markup(owned_lists)
                         )
    else:
        bot.send_message(msg.chat.id,
                         'You do not currently own any lists.\n\nPlease create a list by visiting our beloved *List Management* using the /lists command :)!',
                         parse_mode="Markdown",
                         )


def show_lists(msg):
    # TODO: Enforce authentication - only do sth if tg user has connected his acc to an existing zv acc
    # get connected zv account user
    zv_user = find_connected_zv_user(msg)
    owned_lists = get_all_lists(zv_user)

    list_output_string = ""
    list_count = 0

    for list in owned_lists:
        if list['description'] is not None:
            list_output_string += "Title: {}\nDescription: {}\n\n".format(
                list['title'], list['description'])
        else:
            list_output_string += "Title: {}\n\n".format(list['title'])
        list_count += 1

    if list_count > 0:
        bot.send_message(msg.chat.id,
                         'You are currently the owner of the following {} list(s):\n\n_{}_'.format(
                             list_count,
                             list_output_string),
                         parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id,
                         'You do not currently own any lists.\n\nPlease create a list by visiting our beloved *List Management* using the /lists command :)!',
                         parse_mode="Markdown",
                         )


# e.g. /caps what up dawg?! -> ['what', 'up', 'dawg?!']
def extract_args(msg):
    return msg.split()[1:]


# setup webhook and any other initialization processes
def init():
    print("[{}] Starting HepiR using (BOT_NAME={}) and (TOKEN={}) now...".format(
        str(datetime.datetime.now()).split('.')[0], BOT_USERNAME, TOKEN))
    bot.remove_webhook()
    if LOCAL_ENV:
        # bot.infinity_polling()
        bot.polling(none_stop=True)
    else:
        bot.set_webhook(url=WEBHOOK_URL + '/' + TOKEN)


def log_callback_query(call):
    msg = call.message
    print(
        "[{}] Received '{}' call.data from '{}' (ID={})".format(str(datetime.datetime.now()).split('.')[0],
                                                                call.data,
                                                                (str(msg.from_user.first_name) + " " + str(
                                                                    msg.from_user.last_name)) if msg.from_user.last_name is not None else msg.from_user.first_name,
                                                                msg.from_user.id))
    return


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
