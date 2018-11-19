from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data=f"cb_yes"),
               InlineKeyboardButton("No", callback_data=f"cb_no"))
    return markup