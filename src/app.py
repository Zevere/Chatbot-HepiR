import telebot

TOKEN = "752142027:AAGCp47hpBa3LYkBgEXMUlftOABpndyqwOM"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    text = message.text
    msg = bot.send_message(chat_id, 'How old are you?')
    bot.register_next_step_handler(msg, askAge)


def askAge(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Age must be a number, enter again.')
        bot.register_next_step_handler(msg, askAge)
        return
    bot.send_message(chat_id, 'Thank you, I remembered that you are {} y/o.'.format(text))


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


bot.polling()
