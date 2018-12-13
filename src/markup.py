from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


def hide_inline_keyboard_markup():
    return None


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


def task_management_markup(selected_list_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("View all tasks in the list",
                             callback_data='cb_vtask_{}'.format(selected_list_id)),
        InlineKeyboardButton("Add a new task to the list",
                             callback_data='cb_atask_{}'.format(selected_list_id)),
        # dptsk = delete task but need to pick from existing first
        InlineKeyboardButton("Delete an existing task from the list",
                             callback_data='cb_dptsk_{}'.format(selected_list_id)),
        InlineKeyboardButton("Choose another list",
                             callback_data="cb_selectList"),
    )
    return markup


def delete_task_markup(existing_tasks):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for task in existing_tasks[:]:
        # max cb data len is 64 characters
        markup.add(
            InlineKeyboardButton(
                task['title'], callback_data="cb_dtask_{}".format(task['id'])),
        )
    return markup


def delete_list_markup(existing_lists):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for list in existing_lists[:]:
        # had to use dlist instead of more descriptive delete_list
        # due to telegram limitation which would cause BUTTON_DATA_INVALID error
        # max cb data len is 64 characters
        markup.add(
            InlineKeyboardButton(
                list['title'], callback_data="cb_dlist_{}".format(list['id'])),
        )
    return markup


def select_list_markup(existing_lists):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for list in existing_lists[:]:
        # max cb data len is 64 characters
        markup.add(
            InlineKeyboardButton(
                list['title'], callback_data="cb_slist_{}".format(list['id'])),
        )
    return markup


def confirm_delete_list_markup(selected_list_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            # callback_data headers must be 9 length in this app's design
            'Yes', callback_data='cb_ydlst_{}'.format(selected_list_id)),
        InlineKeyboardButton(
            'No', callback_data='cb_ndlst_{}'.format(selected_list_id)),
    )
    return markup


def confirm_delete_task_markup(selected_task_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(
            # callback_data headers must be 9 length in this app's design
            'Yes', callback_data='cb_ydtsk_{}'.format(selected_task_id)),
        InlineKeyboardButton(
            'No', callback_data='cb_ndtsk_{}'.format(selected_task_id)),
    )
    return markup


def confirm_create_list_markup(list_title):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(
            # callback_data headers must be 9 length in this app's design
            'Yes', callback_data='cb_yclst_{}'.format(list_title)),
        InlineKeyboardButton(
            'No', callback_data='cb_nclst_{}'.format(list_title)),
    )
    return markup


def confirm_create_task_markup(task_title):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(
            # callback_data headers must be 9 length in this app's design
            'Yes', callback_data='cb_yatsk_{}'.format(task_title)),
        InlineKeyboardButton(
            'No', callback_data='cb_natsk_{}'.format(task_title)),
    )
    return markup
