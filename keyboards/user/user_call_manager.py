from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.button(text='Позвать LuxManager', callback_data=f'call_manager')

builder.adjust(1)

call_manager_menu_ru = builder.as_markup()

builder2 = InlineKeyboardBuilder()
builder2.button(text='Call LuxManager', callback_data=f'call_manager')

builder2.adjust(1)

call_manager_menu_en = builder2.as_markup()