from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def list_management_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("View all my lists", callback_data="cb_viewLists"),
        InlineKeyboardButton("Create a new list", callback_data="cb_createList"),
        InlineKeyboardButton("Delete an existing list", callback_data="cb_deleteList"),
        InlineKeyboardButton("Select an existing list", callback_data="cb_selectList"),
    )
    return markup
