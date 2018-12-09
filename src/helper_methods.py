import requests
from properties import *
import datetime
from markup import *
from pprint import pprint
from list_management import (
    create_list,
    get_all_lists,
    delete_list,
)


def remove_reply_keyboard(tbot, cb_call):
    tbot.edit_message_reply_markup(
        chat_id=cb_call.message.chat.id, message_id=cb_call.message.json['message_id'], reply_markup=hide_inline_keyboard_markup())


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
