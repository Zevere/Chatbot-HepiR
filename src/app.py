import telebot
import bs4
from src.Task import Task
import src.Parser as parser
import src.markups as m

# main variables
bot = telebot.TeleBot(TOKEN)
task = Task()


# handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    if not task.isRunning:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, 'Where to parse?', reply_markup=m.source_markup)
        bot.register_next_step_handler(msg, askSource)
        task.isRunning = True


def askSource(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if text in task.names[0]:
        task.mySource = 'top'
        msg = bot.send_message(chat_id, 'For what time period?', reply_markup=m.age_markup)
        bot.register_next_step_handler(msg, askAge)
    elif text in task.names[1]:
        task.mySource = 'all'
        msg = bot.send_message(chat_id, 'What is the minimum rating threshold?')
        bot.register_next_step_handler(msg, askRating)
    else:
        msg = bot.send_message(chat_id, 'Enter the section correctly.')
        bot.register_next_step_handler(msg, askSource)
        return


def askAge(message):
    chat_id = message.chat.id
    text = message.text.lower()
    filters = task.filters[0]
    if text not in filters:
        msg = bot.send_message(chat_id, 'There is no such time interval. Please enter the threshold correctly.')
        bot.register_next_step_handler(msg, askAge)
        return
    # task.myFilter = task.filters_code_names[0][filters.index(text)]
    msg = bot.send_message(chat_id, 'How many pages are we parsing?')
    bot.register_next_step_handler(msg, askAmount)


def askRating(message):
    chat_id = message.chat.id
    text = message.text.lower()
    filters = task.filters[1]
    if text not in filters:
        msg = bot.send_message(chat_id, 'There is no such threshold, enter the threshold correctly.')
        bot.register_next_step_handler(msg, askRating)
        return
    # task.myFilter = task.filters_code_names[1][filters.index(text)]
    msg = bot.send_message(chat_id, 'How many pages are we parsing?')
    bot.register_next_step_handler(msg, askAmount)


def askAmount(message):
    chat_id = message.chat.id
    text = message.text.lower()
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'The number of pages must be a number. Please enter the correct number.')
        bot.register_next_step_handler(msg, askAmount)
        return
    if int(text) < 1 or int(text) > 11:
        msg = bot.send_message(chat_id, 'The number of pages must be > 0 and <11. Enter correctly.')
        bot.register_next_step_handler(msg, askAmount)
        return
    task.isRunning = False
    output = ''
    if task.mySource == 'top':
        output = parser.getTitlesFromTop(int(text), task.myFilter)
    else:
        output = parser.getTitlesFromAll(int(text), task.myFilter)
    print("output is {}".format(output))
    msg = bot.send_message(chat_id, output)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    if text == 'hello':
        bot.send_message(chat_id, "Hello, I'm a bot-a huber parser.")
    elif text == 'how are you?':
        bot.send_message(chat_id, "Ok, and you?")
    else:
        bot.send_message(chat_id, "Sorry, I did not understand :(")


# content-types include: text, audio, document, photo, sticker, video, video_note, voice, location, contact, new_chat_members, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created, supergroup_chat_created, channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, pinned_message
@bot.message_handler(content_types=['photo'])
def text_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Beautiful.')


bot.polling(none_stop=True)
