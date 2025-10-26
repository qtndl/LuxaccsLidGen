from aiogram import types, Router, F
from aiogram.filters import Command
from typing import Union
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
from config.bot_config import bot, CHAT_ID
from sqlalchemy import select, and_, func, or_, text

from database.database import AsyncSessionLocal
from database.models import Users

from keyboards.user.new_user_topic import manager_took_usr_in_work_keyboard

router = Router(name='in_topic_router')

@router.callback_query(F.data.startswith('mngr_'))
async def ignore_button(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_username = callback.from_user.username
    user_fullname = callback.from_user.full_name

    client_id = int(callback.data.split('_')[-1])
    msg_id = callback.message.message_id

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users).where(Users.telegram_id==int(client_id)))
        user = record.scalar_one_or_none()
        user.manager_id = str(user_id)
        user.manager_username = user_username
        user.manager_full_name = user_fullname
        await session.commit()

    await bot.edit_message_reply_markup(chat_id=CHAT_ID, message_id=msg_id, reply_markup=manager_took_usr_in_work_keyboard)


@router.message(F.forum_topic_closed)
async def handle_topic_closed(event: types.Message, bot: bot):

    if event.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    thread_id = event.message_thread_id
    chat_id = CHAT_ID

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users.telegram_id).where(Users.thread_id==int(thread_id)))
        user_id = record.scalar_one_or_none()
    if user_id:
        await bot.send_message(chat_id=user_id, text='✅ Обращение закрыто')

@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_group_message(message: types.Message, bot: bot):

    if not message.message_thread_id or message.from_user.id == bot.id:
        return

    try:
        async with AsyncSessionLocal() as session:
            record = await session.execute(select(Users.telegram_id).where(Users.thread_id==int(message.message_thread_id)))
            user_id = record.scalar_one_or_none()

        # Копируем сообщение пользователю
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

    except Exception as e:
        await message.answer('❌ Ошибка пересылки сообщения. Обратитесь к разработчику.')
        print(f"Ошибка пересылки сообщения пользователю: {e}")

@router.message(F.chat.type == ChatType.PRIVATE)
async def handle_user_reply(message: types.Message, bot: bot):
    user_id = str(message.from_user.id)
    try:
        async with AsyncSessionLocal() as session:
            record = await session.execute(select(Users.thread_id).where(Users.telegram_id==int(user_id)))
            thread_id = record.scalar_one_or_none()

        if thread_id == 'None':
            await message.answer('❌ У вас нет активных обращений. Используйте /start для создания нового.')
            return

        else:
            await bot.copy_message(
                chat_id=CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                message_thread_id=thread_id
            )

    except Exception as e:
        print(f'Ошибка пересылки сообщения в топик: {e}')
        await message.answer('⚠️ Произошла ошибка при отправке сообщения. Попробуйте позже.')

@router.callback_query(F.data=='ignore')
async def ignore_button(callback: types.CallbackQuery):
    await callback.answer()