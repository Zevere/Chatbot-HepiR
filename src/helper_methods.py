import requests
from properties import *
import datetime
from markup import *
from pprint import pprint

from authentication import (
    is_authenticated,
    get_authenticated_zvuser,
)

from list_management import (
    create_list,
    get_all_lists,
    delete_list,
    get_list_by_id,
)

from task_management import(
    get_all_tasks,
    create_task,
    delete_task,
)


def solicit_next_action(msg):
    bot.send_message(
        msg.chat.id, 'How may I further service you today?', reply_markup=next_action_markup())
    pass


def display_task_management(msg):
    connected_user = get_authenticated_zvuser(msg.chat.id)
    selected_list_id = user_collection.find_one(
        {'zv_user': str(connected_user)}).get('selected_list_id')
    selected_list = get_list_by_id(connected_user, selected_list_id)

    bot.send_message(msg.chat.id,
                     "{}\n*Task Management*\n{}\nWelcome to the Task Management Screen!\n\nYou have selected the list with the title of `{}`\n\nHere you will be able to view all of the tasks associated with this list, add new tasks to this list, delete tasks from this list.\n\nWhat would you like to do on this blessed day ☜(⌒▽⌒)☞?".format(
                         '-'*23, '-'*23, selected_list['title']),
                     parse_mode="Markdown",
                     reply_markup=task_management_markup(selected_list_id))


# get tg_id from msg


def enforce_authentication(msg):
    print('Inside enforce_authentication')
    # check if authenticated
    if is_authenticated(msg.chat.id):
        print('\ttg_id {} is authenticated!'.format(msg.chat.id))
        # continues execution of attempted action
        return
    else:
        print('\ttg_id {} is not authenticated!'.format(msg.chat.id))
        # terminate further execution of the attempted action
        bot.send_message(msg.chat.id, 'You are not logged into Zevere. Please login at {} and use the Login Widget provided on the Profile page after logging in :)!'.format(
            COHERENT_ROOT_URL))
        raise Exception


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


def convert_task_title_to_id(task_title):
    return convert_list_title_to_id(task_title)


def handle_create_list_description_force_reply(msg, list_title):
    list_description = msg.text

    if list_description == 'no':
        list_description = None

    zv_user = find_connected_zv_user(msg)
    create_list_results = create_list(zv_user, list_title, list_description)

    if create_list_results[0]:
        bot.send_message(msg.chat.id,
                         'Thank you for your input dear.\n\nYour new list has been successfully created with the following details:\n\nList Title: _{}_\nList Owner: _{}_{}'.format(
                             list_title, zv_user,
                             '\nList Description: _{}_'.format(
                                 list_description) if list_description is not None else ''
                         ),
                         parse_mode="Markdown"
                         )
        solicit_next_action(msg)

    else:
        bot.send_message(msg.chat.id,
                         'An error has occured and the list was not created.',
                         parse_mode="Markdown",)
        solicit_next_action(msg)

    return


def handle_create_task_description_force_reply(msg, task_title):
    task_description = msg.text

    if task_description == 'no':
        task_description = None

    zv_user = find_connected_zv_user(msg)
    selected_list_id = user_collection.find_one(
        {'zv_user': str(zv_user)}).get('selected_list_id')
    create_task_results = create_task(
        zv_user, selected_list_id, task_title, task_description)

    if create_task_results[0]:
        bot.send_message(msg.chat.id,
                         'Thank you for your input dear.\n\nYour new task has been successfully created with the following details:\n\nTask Title: _{}_\nList Owner: _{}_\nList: _{}_{}'.format(
                             task_title, zv_user,
                             get_list_by_id(zv_user, selected_list_id)[
                                 'title'],
                             '\nTask Description: _{}_'.format(
                                 task_description) if task_description is not None else ''
                         ),
                         parse_mode="Markdown"
                         )
        display_task_management(msg)

    else:
        bot.send_message(msg.chat.id,
                         'An error has occured and the task was not created.',
                         parse_mode="Markdown",)
        display_task_management(msg)

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


def handle_create_task_id_force_reply(msg, zv_user, list_id):
    """Solicits task title from user, then prompts user for task creation confirmation.
    """
    task_title = msg.text
    task_id = convert_list_title_to_id(task_title)
    print('\task_title={}\nlist_id={}'.format(task_title, task_id))
    print('len of the task_id={}\nValid len id={}\n'.format(
        len(task_id), is_valid_id_len(task_id)[0]))

    within_bounds, leftover_char_limit = is_valid_id_len(task_id)

    if within_bounds:
        # check that the list does not already contain the task that the user is trying to add
        existing_tasks = get_all_tasks(zv_user, list_id)

        for task in existing_tasks:
            if task['id'] == task_id:
                bot.send_message(msg.chat.id, 'Your selected list already contains a task created with the title of _{}_!\n\nYou cannot add duplicate tasks with the same title in Zevere.\n\nPlease try again with a different name :)!'.format(
                    task_title),
                    parse_mode="Markdown"
                )
                display_task_management(msg)
                return

        bot.send_message(msg.chat.id,
                         'Are you sure you want to `add` this task to the selected list?\n\nYour new task will have a title of _{}_'.format(
                             task_title),
                         parse_mode="Markdown",
                         reply_markup=confirm_create_task_markup(task_title)
                         )
    else:
        bot.send_message(msg.chat.id,
                         'Your title is too long!The maximum number of characters permitted for a task title is 55 characters.\n\nYour task title exceeded this amount by *{}* characters.\n\nPlease return to Task Management (/lists and selecting your list) and try again with a different title :)'.format(
                             abs(leftover_char_limit)),
                         parse_mode="Markdown"
                         )
        display_task_management(msg)
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
        solicit_next_action(msg)

    else:
        bot.send_message(msg.chat.id,
                         'An error has occured and the list was not deleted.',
                         parse_mode="Markdown",)
        solicit_next_action(msg)


def delete_task_confirm_btn_clicked(msg, task_id):
    zv_user = find_connected_zv_user(msg)
    selected_list_id = user_collection.find_one(
        {'zv_user': str(zv_user)}).get('selected_list_id')

    print('\n\nTrying to delete task with id = {} from selected list with id = {}\n'.format(
        task_id, selected_list_id))

    delete_task_results = delete_task(zv_user, selected_list_id, task_id)

    if(delete_task_results[0]):
        bot.send_message(msg.chat.id,
                         'The task with the id `{}` was successfully deleted.'.format(
                             delete_task_results[1]),
                         parse_mode="Markdown",)
        display_task_management(msg)

    else:
        bot.send_message(msg.chat.id,
                         'An error has occured and the task was not deleted.',
                         parse_mode="Markdown",)
        display_task_management(msg)
    return


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


def show_lists_to(action, msg):
    zv_user = find_connected_zv_user(msg)
    owned_lists = get_all_lists(zv_user)
    if len(owned_lists) > 0:
        bot.send_message(msg.chat.id,
                         'Please click on the list you wish to `{}`:'.format(
                             action),
                         parse_mode="Markdown",
                         reply_markup=delete_list_markup(
                             owned_lists) if action == 'delete' else select_list_markup(owned_lists)
                         )
    else:
        bot.send_message(msg.chat.id,
                         'You do not currently own any lists.\n\nPlease create a list by visiting our beloved *List Management* using the /lists command :)!',
                         parse_mode="Markdown",
                         )


def show_lists_to_select(msg):
    show_lists_to('select', msg)
    return


def show_lists_to_delete(msg):
    show_lists_to('delete', msg)
    return


def show_lists(msg):
    # TODO: Enforce authentication - only do sth if tg user has connected his acc to an existing zv acc
    # get connected zv account user
    zv_user = find_connected_zv_user(msg)
    owned_lists = get_all_lists(zv_user)

    lists_output_string = ""
    list_count = 0

    for list in owned_lists:
        if list['description'] is not None:
            lists_output_string += "Title: {}\nDescription: {}\n\n".format(
                list['title'], list['description'])
        else:
            lists_output_string += "Title: {}\n\n".format(list['title'])
        list_count += 1

    if list_count > 0:
        bot.send_message(msg.chat.id,
                         'You are currently the owner of the following {} list(s):\n\n_{}_'.format(
                             list_count,
                             lists_output_string),
                         parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id,
                         'You do not currently own any lists.\n\nPlease create a list by visiting our beloved *List Management* using the /lists command :)!',
                         parse_mode="Markdown",
                         )


def show_tasks_to_delete(msg, list_id):
    zv_user = find_connected_zv_user(msg)
    existing_tasks = get_all_tasks(zv_user, list_id)
    if len(existing_tasks) > 0:
        bot.send_message(msg.chat.id,
                         'Please click on the task you wish to `delete`:',
                         parse_mode="Markdown",
                         reply_markup=delete_task_markup(
                             existing_tasks)
                         )
    else:
        bot.send_message(msg.chat.id,
                         'There are currently no tasks part of the selected list.\n\nPlease add a task to the selected list by visiting our beloved *Task Management* by using the /lists command and selecting a list from there :)!',
                         parse_mode="Markdown",
                         )


def show_tasks(msg, list_id):
    zv_user = find_connected_zv_user(msg)
    existing_tasks = get_all_tasks(zv_user, list_id)

    tasks_output_string = ""
    task_count = 0

    for task in existing_tasks:
        if task['description'] is not None:
            tasks_output_string += "Title: {}\nDescription: {}\n\n".format(
                task['title'], task['description'])
        else:
            tasks_output_string += "Title: {}\n\n".format(task['title'])
        task_count += 1

    if task_count > 0:
        bot.send_message(msg.chat.id,
                         'There are currently the following {} task(s) within the selected list:\n\n_{}_'.format(
                             task_count,
                             tasks_output_string),
                         parse_mode="Markdown")
    else:
        bot.send_message(msg.chat.id,
                         'There are currently no tasks part of the selected list.\n\nPlease add a task to the selected list by visiting our beloved *Task Management* by using the /lists command and selecting a list from there :)!',
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
