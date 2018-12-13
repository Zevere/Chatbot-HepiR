from markup import *
from hepir_logging import (
    log_callback_query,
    log_command_info,
    log_inline_query_info,
    log_received_text_msg,
)
from authentication import(
    connect,
    disconnect,
    get_authenticated_zvuser,
)
from list_management import(
    get_list_by_id,
)

# Flask Routes ------------------------------------------------------------------------------------------
from flask_routes import *

# Helper methods ------------------------------------------------------------------------------------------
from helper_methods import(
    show_lists,
    handle_create_list_description_force_reply,
    show_lists_to_delete,
    handle_create_list_id_force_reply,
    remove_reply_keyboard,
    delete_list_confirm_btn_clicked,
    init,
    show_lists_to_select,
    show_tasks,
    handle_create_task_id_force_reply,
    handle_create_task_description_force_reply,
    show_tasks_to_delete,
    delete_task_confirm_btn_clicked,
)

# Telegram Bot Message Handlers --------------------------------------------------------------------------


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    log_callback_query(call)

    if call.data == "cb_viewLists":
        bot.answer_callback_query(call.id, "Here are your lists \(ᵔᵕᵔ)/")
        show_lists(call.message)

    elif call.data == "cb_createList":
        bot.answer_callback_query(call.id, "Let's create a new list \o/!!")
        sent = bot.send_message(
            call.message.chat.id, 'Please enter in the title of your new list:', reply_markup=telebot.types.ForceReply())
        bot.register_next_step_handler(sent, handle_create_list_id_force_reply)

    elif call.data == "cb_deleteList":
        bot.answer_callback_query(call.id, "Please select a list to delete :)")
        show_lists_to_delete(call.message)

    elif call.data == "cb_selectList":
        bot.answer_callback_query(call.id, "Please select a list to select :)")
        show_lists_to_select(call.message)

    else:
        # delete a list e.g. cb_dlist_<listid>
        if call.data.find('cb_dlist_') != -1:
            selected_list_id = call.data[len('cb_dlist_'):]
            bot.answer_callback_query(
                call.id, "You clicked on the list with id={}".format(selected_list_id))
            sent = bot.send_message(call.message.chat.id,
                                    'Are you sure you want to `delete` this list?\nList with id of *{}*'.format(
                                        selected_list_id),
                                    parse_mode="Markdown",
                                    reply_markup=confirm_delete_list_markup(selected_list_id))

        # selected a list to see more details e.g. tasks within the list
        elif call.data.find('cb_slist_') != -1:
            selected_list_id = call.data[len('cb_slist_'):]
            connected_user = get_authenticated_zvuser(call.message.chat.id)
            selected_list = get_list_by_id(connected_user, selected_list_id)

            # Need to update hepir db to store the currently selected list
            # because of limitation of 64 characters, won't be able to pass in
            # list id and task id in callback data later when creating a task
            # or deleting a task
            user_collection.update_one(
                {'tg_id': str(call.message.chat.id)},
                {
                    "$set": {
                        "selected_list_id": selected_list_id,
                    }
                }
            )

            bot.answer_callback_query(
                call.id, "You clicked on the list with id={}".format(selected_list_id))
            bot.send_message(call.message.chat.id,
                             "{}\n*Task Management*\n{}\nWelcome to the Task Management Screen!\n\nYou have selected the list with the title of `{}`\n\nHere you will be able to view all of the tasks associated with this list, add new tasks to this list, delete tasks from this list.\n\nWhat would you like to do on this blessed day ☜(⌒▽⌒)☞?".format(
                                 '-'*23, '-'*23, selected_list['title']),
                             parse_mode="Markdown",
                             reply_markup=task_management_markup(selected_list_id))

        # confirm delete list
        elif call.data.find('cb_ydlst_') != -1:
            selected_list_id = call.data[len('cb_ydlst_'):]
            bot.answer_callback_query(
                call.id, "You confirmed to delete the list with id={}".format(selected_list_id))
            remove_reply_keyboard(bot, call)
            delete_list_confirm_btn_clicked(call.message, selected_list_id)

        # reject delete list
        elif call.data.find('cb_ndlst_') != -1:
            bot.answer_callback_query(call.id, "Cancelled Action")
            remove_reply_keyboard(bot, call)
            bot.send_message(
                call.message.chat.id, "Okay, the list was not deleted.\nHow may I help you today?", reply_markup=telebot.types.ReplyKeyboardRemove())
            # TODO return markup k/b with buttons for each of the /commands

        # confirm create list
        elif call.data.find('cb_yclst_') != -1:
            task_title = call.data[len('cb_yclst_'):]
            bot.answer_callback_query(
                call.id, "You confirmed to create the list with title of {}".format(task_title))
            remove_reply_keyboard(bot, call)
            sent = bot.send_message(
                call.message.chat.id, 'Great! Thank you for confirming.\nThat is a fantastic title for your new list 8D!\n\nWould you like to add a description to your newly created list?\n\nIf you would not like to add a description, please kindly reply *no*:',
                parse_mode='Markdown',
                reply_markup=telebot.types.ForceReply())
            bot.register_next_step_handler(
                sent, handle_create_list_description_force_reply, task_title)

        # reject create list
        elif call.data.find('cb_nclst_') != -1:
            bot.answer_callback_query(call.id, "Cancelled Action")
            remove_reply_keyboard(bot, call)
            bot.send_message(
                call.message.chat.id, "Okay, the list was not created.\nHow may I help you today?")
            # TODO return markup k/b with buttons for each of the /commands

        # view tasks within the selected list
        elif call.data.find('cb_vtask_') != -1:
            selected_list_id = call.data[len('cb_vtask_'):]
            bot.answer_callback_query(call.id, "Here are your tasks ᕙ(⇀‸↼‶)ᕗ")
            show_tasks(call.message, selected_list_id)

        # add a task to the selected list
        elif call.data.find('cb_atask_') != -1:
            selected_list_id = call.data[len('cb_atask_'):]
            connected_user = get_authenticated_zvuser(call.message.chat.id)

            bot.answer_callback_query(call.id, "Let's create a new task \o/!!")
            sent = bot.send_message(
                call.message.chat.id, 'Please enter in the title of your new task:', reply_markup=telebot.types.ForceReply())
            bot.register_next_step_handler(
                sent, handle_create_task_id_force_reply, connected_user, selected_list_id)

        # choose an existing task from the selected list to delete
        elif call.data.find('cb_dptsk_') != -1:
            selected_list_id = call.data[len('cb_dptsk_'):]
            bot.answer_callback_query(
                call.id, "Please select a list to delete :)")
            show_tasks_to_delete(call.message, selected_list_id)

        # delete a task e.g. cb_dtask_<taskid>
        elif call.data.find('cb_dtask_') != -1:
            selected_task_id = call.data[len('cb_dtask_'):]
            bot.answer_callback_query(
                call.id, "You clicked on the task with id={}".format(selected_task_id))
            sent = bot.send_message(call.message.chat.id,
                                    'Are you sure you want to `delete` this task from the selected list?\nTask with id of *{}*'.format(
                                        selected_task_id),
                                    parse_mode="Markdown",
                                    reply_markup=confirm_delete_task_markup(selected_task_id))

        # confirm delete task
        elif call.data.find('cb_ydtsk_') != -1:
            selected_task_id = call.data[len('cb_ydtsk_'):]
            bot.answer_callback_query(
                call.id, "You confirmed to delete the task with id={} from the selected list.".format(selected_task_id))
            remove_reply_keyboard(bot, call)
            delete_task_confirm_btn_clicked(call.message, selected_task_id)

        # reject delete task
        elif call.data.find('cb_ndtsk_') != -1:
            bot.answer_callback_query(call.id, "Cancelled Action")
            remove_reply_keyboard(bot, call)
            bot.send_message(
                call.message.chat.id, "Okay, the task was not deleted from the selected list.\nHow may I help you today?", reply_markup=telebot.types.ReplyKeyboardRemove())
            # TODO return markup k/b with buttons for each of the /commands

        # confirm create task
        elif call.data.find('cb_yatsk_') != -1:
            task_title = call.data[len('cb_yatsk_'):]
            bot.answer_callback_query(
                call.id, "You confirmed to add the task with title of {}".format(task_title))
            remove_reply_keyboard(bot, call)
            sent = bot.send_message(
                call.message.chat.id, 'Great! Thank you for confirming.\nThat is a fantastic title for your new task 8D!\n\nWould you like to add a description to your newly created task?\n\nIf you would not like to add a description, please kindly reply *no*:',
                parse_mode='Markdown',
                reply_markup=telebot.types.ForceReply())

            bot.register_next_step_handler(
                sent, handle_create_task_description_force_reply, task_title)

        # reject create task
        elif call.data.find('cb_natsk_') != -1:
            bot.answer_callback_query(call.id, "Cancelled Action")
            remove_reply_keyboard(bot, call)
            bot.send_message(
                call.message.chat.id, "Okay, the task was not created.\nHow may I help you today?")
            # TODO return markup k/b with buttons for each of the /commands

        else:
            bot.answer_callback_query(
                call.id, "You clicked on the list with id={}".format(call.data))


@bot.message_handler(commands=['lists'])
def list_management(msg):
    log_command_info('/lists', msg)

    bot.send_message(msg.chat.id,
                     "{}\n*List Management*\n{}\nWelcome to the List Management Screen!\n\nHere you are able to create new lists, view all of your lists, delete an existing list, and select a list to view its list items and/or add new tasks to the list.\n\nWhat would you like to do on this blessed day ٩(⁎❛ᴗ❛⁎)۶?".format(
                         '-'*23, '-'*23),
                     parse_mode="Markdown",
                     reply_markup=list_management_markup())
    return


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
        #     e.g. GET VIVID_ROOT_URL/api/v1/operations/getUserProfile/?username=kevin.ma
        vivid_request = requests.get(
            '{}/api/v1/operations/getUserProfile/'.format(VIVID_ROOT_URL), params={'username': zv_user},
            auth=(VIVID_USER, VIVID_PASSWORD))

        resp = vivid_request.json()

        fname = resp.get('firstName')
        zv_user = resp.get('id')
        lname = resp.get('lastName')

        print('found this resp:')
        pprint(resp)

        bot.send_message(msg.chat.id,
                         'You are logged in as *{} {}* (`{}`).'.format(fname, lname, zv_user), parse_mode="Markdown")

    # zv user - tg user connection not found in hepir db => add connection to hepir db
    else:
        print(
            '[{}] No connections found matching (tg_id={}) in (db={})'.format(
                str(datetime.datetime.now()).split('.')[0], tg_id, MONGODB_DBNAME))

        bot.send_message(msg.chat.id,
                         'You are not logged into Zevere. Please login at {} and use the Login Widget provided on the Profile page after logging in :)!'.format(COHERENT_ROOT_URL))


@bot.message_handler(commands=['logout'])
def logout(msg):
    log_command_info('/logout', msg)
    tg_id = msg.chat.id
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})
    zv_user = found_connection.get('zv_user')
    disconnect(zv_user, tg_id, bot=bot, msg=msg)
    return

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
        #     e.g. GET VIVID_ROOT_URL/api/v1/operations/getUserProfile/?username=kevin.ma
        vivid_request = requests.get(
            '{}/api/v1/operations/getUserProfile/'.format(VIVID_ROOT_URL), params={'username': zv_user},
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
                         'You are not logged into Zevere. Please login at {} and use the Login Widget provided on the Profile page after logging in :)!'.format(COHERENT_ROOT_URL))


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
                     "HepiR - v{}\nLately, I've been, I've been thinking\nI want you to be happier, I want you to use Zevere!~\n\nI understand the follow commands:\n{}\n\n...and I echo all regular messages you send to me so you will never be lonely ;).".format(
                         VERSION, KNOWN_COMMANDS))
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
        bot.reply_to(
            msg, 'Sorry, I did not understand the command: {}'.format(msg.text))
    else:
        bot.reply_to(msg, msg.text)


if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=PORT)
