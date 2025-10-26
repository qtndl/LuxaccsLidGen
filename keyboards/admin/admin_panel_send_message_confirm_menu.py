from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

builder = InlineKeyboardBuilder()

button_delete_message = InlineKeyboardButton(text='Да',
                                          callback_data='admin_send_message_confirm')

builder.row(button_delete_message)

admin_panel_send_message_confirm_menu = builder.as_markup()