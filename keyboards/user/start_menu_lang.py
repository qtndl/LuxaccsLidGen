from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.button(text='🇷🇺 Русский', callback_data=f'ru')
builder.button(text='🇬🇧 English', callback_data=f'en')


builder.adjust(2)

start_menu_lang = builder.as_markup()