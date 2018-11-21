import requests
from src.properties import *
import datetime


def show_lists(msg):
    print("I am in helper_methods.show_lists()")
    # TODO: Enforce authentication - only do sth if tg user has connected his acc to an existing zv acc
    # get connected zv account user
    tg_id = msg.chat.id
    print("tg_id={}".format(tg_id))
    print("user_collection={}".format(user_collection))
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})

    print("found_connection={}".format(found_connection))

    if found_connection:
        zv_user = found_connection.get('zv_user')

    print("zv_user={}".format(zv_user))

    # send POST request to borzoo graphql web api to query lists belonging to connected zv user
    response = requests.post('https://zv-s-webapi-borzoo.herokuapp.com/zv/graphql',
                             json=
                             {
                                 "query": "query{ user(userId:\"" + zv_user + "\") { lists { id collaborators createdAt description owner tags tasks { id } title updatedAt } } }"
                             },
                             headers={'Content-Type': 'application/json'})

    if response.status_code == 200:
        response = response.json()
        print('response: {}'.format(response))
        owned_lists = response['data']['user']['lists']

        list_output_string = ""
        list_count = 0

        for list in owned_lists:
            list_output_string += "Title: {}\nDescription: {}\n\n".format(list['title'], list['description'])
            list_count += 1

        if 'ican put fake id here that alrady exists? suka blyat' in list_output_string:
            print('list with id of \"{}\" already exists as a list owned by {}'.format(
                'ican put fake id here that alrady exists? suka blyat', zv_user))
        else:
            print('list with id of \"{}\" will now be created with the owner as {}'.format(
                'ican put fake id here that alrady exists? suka blyat', zv_user))

    bot.send_message(msg.chat.id,
                     'As you are connected to your Zevere account (`{}`), you are currently the owner of the following {} lists:\n\n_{}_'.format(
                         zv_user, list_count,
                         list_output_string),
                     parse_mode="Markdown")


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
