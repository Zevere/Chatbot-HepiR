import src.markup as m

# Flask Routes ------------------------------------------------------------------------------------------
from src.flask_routes import *

# Helper methods ------------------------------------------------------------------------------------------
from src.helper_methods import *


# Telegram Bot Command Handlers --------------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")


@bot.message_handler(commands=['q'])
def message_handler(message):
    bot.send_message(message.chat.id, "Yes/no?", reply_markup=m.gen_markup())


# no args /lists displays lists owned by connected zv account user
# args with /lists "selects" the list if the listname in args exists and is owned by the connected zv account user
@bot.message_handler(commands=['lists'])
def show_lists(msg):
    log_command_info('/lists', msg)

    # TODO: Enforce authentication - only do sth if tg user has connected his acc to an existing zv acc
    # get connected zv account user
    tg_id = msg.chat.id
    found_connection = user_collection.find_one({'tg_id': str(tg_id)})

    if found_connection:
        zv_user = found_connection.get('zv_user')

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


if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=PORT)
