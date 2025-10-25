from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


async def new_user_topic_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text='Взять в работу', callback_data=f'mngr_{user_id}')

    builder.adjust(1)

    keyboard = builder.as_markup()
    return keyboard

builder_2 = InlineKeyboardBuilder()
builder_2.button(text='✅ В работе', callback_data=f'ignore')

builder_2.adjust(1)

manager_took_usr_in_work_keyboard = builder_2.as_markup()
