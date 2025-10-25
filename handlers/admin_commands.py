from aiogram import types, Router, F
from aiogram.filters import Command
from typing import Union
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config.bot_config import bot
from sqlalchemy import select, and_, func, or_, text

from database.database import AsyncSessionLocal
from database.models import Users
from keyboards.main_menu_builder import main_menu_builder
from keyboards.user.start_menu_lang import start_menu_lang

router = Router(name='start_router')

@router.message(Command("add_admin"))
async def add_admin(message: types.Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users.user_role).where(Users.telegram_id==int(user_id)))
        user_role = record.scalar_one_or_none()

    if user_role != 'admin':
        await message.answer(f'❌ Нет прав администратора!\n'
                             f'Попросите администратора дать вам права админа.\n'
                             f'Отправьте ему свой Telegram ID: <code>{user_id}</code>', parse_mode='HTML')
        return

    id_to_add = message.text.split()[-1]

    if id_to_add==message.text:
        await message.answer('❌ Нужно отправить команду в формате:\n'
                             '/add_admin [telegram id]\n\n'
                             'Например: /add_admin 456879841')
        return

    async with AsyncSessionLocal() as admin_session:
        record = await admin_session.execute(select(Users).where(Users.telegram_id==int(id_to_add)))
        user = record.scalar_one_or_none()

        if user is None:
            await message.answer('❌ Пользователя нет в базе данных, не получилось выдать права админа!\n'
                                 'Пользователю нужно зайти в бота и выбрать язык, тогда он попадет в базу данных')
            return
        user.user_role = 'admin'
        await admin_session.commit()

        await message.answer(f'✅ Пользователь ({user.full_name}|@{user.telegram_username}) получил права админа.')

@router.message(Command("stat"))
async def admin_stat(message: types.Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users.user_role).where(Users.telegram_id==int(user_id)))
        user_role = record.scalar_one_or_none()

    if user_role != 'admin':
        await message.answer(f'❌ Нет прав администратора!\n'
                             f'Попросите администратора дать вам права админа.\n'
                             f'Отправьте ему свой Telegram ID: <code>{user_id}</code>', parse_mode='HTML')
        return

    id_to_stat = message.text.split()[-1]

    if id_to_stat==message.text:
        await message.answer('❌ Нужно отправить команду в формате:\n'
                             '/stat [telegram id клиента]\n\n'
                             'Например: /stat 456879841')
        return

    async with AsyncSessionLocal() as admin_session:
        record = await admin_session.execute(select(Users).where(Users.telegram_id==int(id_to_stat)))
        user = record.scalar_one_or_none()

        if user is None:
            await message.answer('❌ Пользователя нет в базе данных!\n'
                                 'Пользователю нужно зайти в бота и выбрать язык, тогда он попадет в базу данных')
            return

        client_username = user.telegram_username
        client_lang = user.user_lang
        client_manager = user.manager_username
    async with AsyncSessionLocal() as ref_session:
        record = await ref_session.execute(select(func.count(Users.id)).where(Users.ref==int(id_to_stat)))
        ref_count = record.scalar()
        if ref_count is None:
            ref_count = 0

    await message.answer(f'Статистика по пользователю c ID {id_to_stat}\n\n'
                         f'Юзернейм: @{client_username}\n'
                         f'Выбранный язык: {client_lang}\n'
                         f'Менеджер: @{client_manager}\n'
                         f'Привлечено лидов: {ref_count}')






