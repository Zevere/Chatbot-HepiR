from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def list_management_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("View all my lists",
                             callback_data="cb_viewLists"),
        InlineKeyboardButton("Create a new list",
                             callback_data="cb_createList"),
        InlineKeyboardButton("Delete an existing list",
                             callback_data="cb_deleteList"),
        InlineKeyboardButton("Select an existing list",
                             callback_data="cb_selectList"),
    )
    return markup


def delete_list_markup(existing_lists):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for list in existing_lists[:]:
        markup.add(
            InlineKeyboardButton("View all my lists",
                                 callback_data="cb_viewLists"),
        )

    markup.add(
        InlineKeyboardButton("View all my lists",
                             callback_data="cb_viewLists"),
        InlineKeyboardButton("Create a new list",
                             callback_data="cb_createList"),
        InlineKeyboardButton("Delete an existing list",
                             callback_data="cb_deleteList"),
        InlineKeyboardButton("Select an existing list",
                             callback_data="cb_selectList"),
    )
    return markup
