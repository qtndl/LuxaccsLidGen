from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from typing import Union
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
from config.bot_config import bot, CHAT_ID
from sqlalchemy import select, and_, func, or_, text
from .google_sheets import find_and_update_by_column_name, add_record_to_sheet
from datetime import datetime

from database.database import AsyncSessionLocal
from database.models import Users

from keyboards.user.new_user_topic import manager_close_client

router = Router(name='in_topic_router')

@router.callback_query(F.data.startswith('mngr_'))
async def mngr_button(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_username = callback.from_user.username
    user_fullname = callback.from_user.full_name

    client_id = int(callback.data.split('_')[-1])
    msg_id = callback.message.message_id

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users).where(Users.telegram_id==int(client_id)))
        user = record.scalar_one_or_none()
        user_lang = user.user_lang
        user.manager_id = str(user_id)
        client_username = user.telegram_username
        client_topic_id = user.thread_id
        user.manager_username = user_username
        user.manager_full_name = user_fullname
        await session.commit()

    if user_lang=='ru':
        text = 'Менеджер подключился к чату'
    else:
        text = 'A manager has joined the chat'
    keyboard = await manager_close_client(client_id)
    await bot.edit_message_reply_markup(chat_id=CHAT_ID, message_id=msg_id, reply_markup=keyboard)
    await bot.send_message(
        chat_id=client_id,
        text=text
    )
    
    await find_and_update_by_column_name(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name='Общий',
        search_column_name='tg_id',
        search_value=f'{client_id}',
        update_column_name='Ответственный менеджер',
        new_value=f'@{user_username}'
    )
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d.%m.%y %H:%M")
    chat_id_for_link = str(CHAT_ID)[4:]
    values_for_sheet = [
        client_id,
        f'@{client_username}',
        formatted_time,
        'Нет',
        ' '
    ]
    await add_record_to_sheet(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name=f'{user_username}',
        values=values_for_sheet
    )

@router.callback_query(F.data.startswith('mcl_'))
async def mngr_close_button(callback: types.CallbackQuery):
    if callback.message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    thread_id = callback.message.message_thread_id
    msg_id = callback.message.message_id

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users).where(Users.thread_id==int(thread_id)))
        user = record.scalar_one_or_none()
        user_lang = user.user_lang
        user_id = user.telegram_id
        user_manager = user.manager_username
        user.thread_id = None
        await session.commit()
    if user_id:
        if user_lang=='ru':
            text = '✅ Обращение закрыто'
        else:
            text = '✅ The inquiry is closed.'
        await bot.send_message(chat_id=user_id, text=text)

    builder = InlineKeyboardBuilder()
    builder.button(text='👌 Клиент закрыт', callback_data=f'ignore')
    builder.adjust(1)
    keyboard = builder.as_markup()

    await bot.edit_message_reply_markup(chat_id=CHAT_ID, message_id=msg_id, reply_markup=keyboard)

    await find_and_update_by_column_name(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name='Общий',
        search_column_name='tg_id',
        search_value=f'{user_id}',
        update_column_name='Закрыт',
        new_value=f'Да'
    )
    await find_and_update_by_column_name(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name=f'{user_manager}',
        search_column_name='tg_id',
        search_value=f'{user_id}',
        update_column_name='Закрыт',
        new_value=f'Да'
    )


@router.message(F.forum_topic_closed)
async def handle_topic_closed(event: types.Message, bot: bot):

    if event.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}:
        return

    thread_id = event.message_thread_id
    chat_id = CHAT_ID

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users).where(Users.thread_id==int(thread_id)))
        user = record.scalar_one_or_none()
        user_lang = user.user_lang
        user_id = user.telegram_id
        user_manager = user.manager_username
        user.thread_id = None
        await session.commit()
    if user_id:
        if user_lang=='ru':
            text = '✅ Обращение закрыто'
        else:
            text = '✅ The inquiry is closed.'
        await bot.send_message(chat_id=user_id, text=text)

    await find_and_update_by_column_name(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name='Общий',
        search_column_name='tg_id',
        search_value=f'{user_id}',
        update_column_name='Закрыт',
        new_value=f'Да'
    )
    await find_and_update_by_column_name(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name=f'{user_manager}',
        search_column_name='tg_id',
        search_value=f'{user_id}',
        update_column_name='Закрыт',
        new_value=f'Да'
    )

@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def handle_group_message(message: types.Message, bot: bot):

    if not message.message_thread_id or message.from_user.id == bot.id:
        return
    if message.message_thread_id is None:
        return

    if (message.new_chat_members or
        message.left_chat_member or
        message.new_chat_title or
        message.new_chat_photo or
        message.delete_chat_photo or
        message.group_chat_created or
        message.supergroup_chat_created or
        message.channel_chat_created or
        message.migrate_to_chat_id or
        message.migrate_from_chat_id or
        message.pinned_message):
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
        await message.answer('❌ Ошибка пересылки сообщения. Возможно, тема уже закрыта. Если это не так - обратитесь к разработчику.')
        print(f"Ошибка пересылки сообщения пользователю: {e}")

@router.message(F.chat.type == ChatType.PRIVATE)
async def handle_user_reply(message: types.Message, bot: bot):
    user_id = str(message.from_user.id)
    try:
        async with AsyncSessionLocal() as session:
            record = await session.execute(select(Users).where(Users.telegram_id==int(user_id)))
            user = record.scalar_one_or_none()
            thread_id = user.thread_id
            user_lang = user.user_lang

        if thread_id is None:
            if user_lang=='ru':
                text = '❌ У вас нет активных обращений. Используйте /start для создания нового.'
            else:
                text = '❌ You have no active inquiries. Use /start to create a new one.'
            await message.answer(text=text)
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