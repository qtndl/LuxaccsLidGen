from aiogram import Bot
from aiogram.types import ForumTopic, Message
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select, and_, func, or_, text

from database.database import AsyncSessionLocal
from database.models import Users
from keyboards.user.new_user_topic import new_user_topic_keyboard


async def create_user_topic(
    bot: Bot,
    chat_id,
    user_name,
    user_id,
    user_tg_name,
    user_lang,
    user_source,
    user_message,
    topic_name):

    try:
        topic = await bot.create_forum_topic(
            chat_id=chat_id,
            name=topic_name
        )

        async with AsyncSessionLocal() as session:
            db_data = await session.execute(select(Users).where(Users.telegram_id==int(user_id)))
            user = db_data.scalar_one_or_none()
            user.thread_id = topic.message_thread_id
            await session.commit()
        keyboard = await new_user_topic_keyboard(user_id)

        await bot.send_message(
            chat_id=chat_id,
            message_thread_id=topic.message_thread_id,
            text=f'Новый лид!\n\n'
                 f'Имя: {user_name}\n'
                 f'Контакт: @{user_tg_name}\n'
                 f'Источник: {user_source}\n'
                 f'Язык: {user_lang}\n\n'
                 f'Опрос:\n'
                 f'{user_message}',
            reply_markup=keyboard)

        return topic

    except TelegramBadRequest as e:
        print(f"Ошибка при создании темы: {e.message}")
        return None

