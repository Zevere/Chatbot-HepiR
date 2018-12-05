import requests
from properties import *
import datetime
from markup import *


def delete_list(zv_user, list_id):
    """Deletes a list belonging to a Zevere user.

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


def create_list(zv_user, list_title, list_desc):
    # TODO
    pass


def is_authenticated(zv_user, tg_id):
    # TODO
    pass


def logout(zv_user, tg_id):
    # TODO
    pass


def delete_list_confirm_btn_clicked(msg, list_id):
    print('\n\nTrying to delete list with id = {}\n'.format(list_id))
    zv_user = find_connected_zv_user(msg)
    delete_results = delete_list(zv_user, list_id)
    if(delete_results[0]):
        bot.send_message(msg.chat.id,
                         'The list with the id `{}` was successfully deleted.'.format(
                             delete_results[1]),
                         parse_mode="Markdown",)
    else:
        bot.send_message(msg.chat.id,
                         'The list was not deleted.',
                         parse_mode="Markdown",)


def find_connected_zv_user(msg):
    """Gets the zevere user account connected to this telegram user.

    Returns:
        Username of the Zevere account if found a connection with the current telegram account. Otherwise, returns None.
    """
    tg_id = msg.chat.id
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})
    if found_connection:
        return found_connection.get('zv_user')
    else:
        return None


def validate_id_len(id):
    """Validates whether passed in id is within 55 character limit boundary.

    Due to telegram bot API restrictions, callback data can at most contain 64 characters. The callback headers in this app have been defined to be 9 chars in length. This leaves 55 char maximum for the variable data length.
    """
    # TODO - need to use this when creating tasks/lists and verify that the id converted from the title will be within the 55 char limit boundary.
    pass


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
                         'You do not currently own any lists. Please create a list by visiting our beloved List Management using the /lists command :)!',
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
        if hasattr(list, 'description'):
            list_output_string += "Title: {}\nDescription: {}\n\n".format(
                list['title'], list['description'])
        else:
            list_output_string += "Title: {}\n\n".format(list['title'])
        list_count += 1

    # if 'ican put fake id here that alrady exists? suka blyat' in list_output_string:
    #     print('list with id of \"{}\" already exists as a list owned by {}'.format(
    #         'ican put fake id here that alrady exists? suka blyat', zv_user))
    # else:
    #     print('list with id of \"{}\" will now be created with the owner as {}'.format(
    #         'ican put fake id here that alrady exists? suka blyat', zv_user))

    if list_count > 0:
        bot.send_message(msg.chat.id,
                         'You are currently the owner of the following {} list(s):\n\n_{}_'.format(
                             list_count,
                             list_output_string),
                         parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id,
                         'You do not currently own any lists. Please create a list by visiting our beloved List Management using the /lists command :)!',
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
