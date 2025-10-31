from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

builder = InlineKeyboardBuilder()

button_delete_message = InlineKeyboardButton(text='Да',
                                          callback_data='admin_send_message_confirm')
button = InlineKeyboardButton(text='Back to menu', callback_data=f'main_menu')

builder.row(button_delete_message)
builder.row(button)

admin_panel_send_message_confirm_menu = builder.as_markup()