from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


async def main_menu_builder(user_role):
    builder = InlineKeyboardBuilder()
    builder.button(text='🎬 Оживить фото', callback_data=f'user_I2V')
    builder.button(text='📋 Прайс', callback_data=f'user_price')
    builder.button(text='➕ Пополнить баланс', callback_data=f'user_balance')
    builder.button(text='📄 Документация', callback_data=f'user_docs')
    builder.button(text='🆘 Поддержка', callback_data=f'user_support')
    if user_role == 'admin':
        builder.button(text='👑 Админ панель', callback_data=f'admin_panel')

    builder.adjust(1)

    keyboard = builder.as_markup()
    return keyboard