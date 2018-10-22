from telebot import types

start_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
start_markup_btn1 = types.KeyboardButton('/start')
start_markup.add(start_markup_btn1)

source_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
source_markup_btn1 = types.KeyboardButton('smart-topics')
source_markup_btn2 = types.KeyboardButton('Webdeveloper-topics')
source_markup.add(source_markup_btn1, source_markup_btn2)

age_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
age_markup_btn1 = types.KeyboardButton('page')
age_markup_btn2 = types.KeyboardButton('')
age_markup_btn3 = types.KeyboardButton('')
age_markup.add(age_markup_btn1, age_markup_btn2, age_markup_btn3)

amount_markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
amount_markup_btn1 = types.KeyboardButton('1')
amount_markup_btn2 = types.KeyboardButton('3')
amount_markup_btn3 = types.KeyboardButton('5')
amount_markup.add(amount_markup_btn1, amount_markup_btn2, amount_markup_btn3)
