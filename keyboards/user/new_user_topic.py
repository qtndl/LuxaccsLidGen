from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


async def new_user_topic_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text='Взять в работу', callback_data=f'mngr_{user_id}')

    builder.adjust(1)

    keyboard = builder.as_markup()
    return keyboard

async def manager_close_client(user_id):
    builder_2 = InlineKeyboardBuilder()
    builder_2.button(text='✅ В работе', callback_data=f'ignore')
    builder_2.button(text='Закрыть клиента', callback_data=f'mcl_{user_id}')

    builder_2.adjust(1)

    keyboard = builder_2.as_markup()
    return keyboard
