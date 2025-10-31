from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.button(text='Назад в меню', callback_data=f'main_menu')


builder.adjust(1)

back_to_main_menu_ru = builder.as_markup()



builder2 = InlineKeyboardBuilder()
builder2.button(text='Back to menu', callback_data=f'main_menu')


builder2.adjust(1)

back_to_main_menu_en = builder2.as_markup()