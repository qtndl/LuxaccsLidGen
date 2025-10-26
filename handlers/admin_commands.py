from aiogram import types, Router, F
from aiogram.filters import Command
import asyncio
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config.bot_config import bot
from sqlalchemy import select, and_, func, or_, text

from database.database import AsyncSessionLocal
from database.models import Users
from keyboards.admin.admin_panel_send_message_confirm_menu import admin_panel_send_message_confirm_menu
from keyboards.user.start_menu_lang import start_menu_lang

router = Router(name='start_router')

class FSM_send_message(StatesGroup):
    sent_message_id = State()
    message_to_send = State()
    confirm = State()

@router.message(Command('send'))
async def admin_send_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users.user_role).where(Users.telegram_id==int(user_id)))
        user_role = record.scalar_one_or_none()

    if user_role != 'admin':
        await message.answer(f'❌ Нет прав администратора!\n'
                             f'Попросите администратора дать вам права админа.\n'
                             f'Отправьте ему свой юзернейм', parse_mode='HTML')
        return

    sent_message = await message.answer(f'Пришлите сообщение для отправки', parse_mode="HTML")
    await state.update_data(sent_message_id=sent_message.message_id)
    await state.set_state(FSM_send_message.message_to_send)


@router.message(FSM_send_message.message_to_send)
async def state_admin_send_message_message(message: types.message, state: FSMContext):
    data = await state.get_data()

    message_text = message.text
    message_to_send = await bot.send_message(chat_id=message.from_user.id,
                                       text=message_text,
                                       # reply_markup=user_panel_keyboard_new_person_babushka,
                                       parse_mode="HTML")
    message_to_send_id = message_to_send.message_id
    await state.update_data(message_to_send=message_to_send_id)

    message_id = str(data['sent_message_id'])
    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)

    await message.answer(f'Подтверждаете отправку сообщения?',
                                        reply_markup=admin_panel_send_message_confirm_menu, parse_mode="HTML")
    await state.set_state(FSM_send_message.confirm)

@router.callback_query(FSM_send_message.confirm, F.data=='admin_send_message_confirm')
async def state_admin_send_message_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    message_to_send = str(data['message_to_send'])

    await state.clear()

    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        users_db = await session.execute(select(Users))
        users = users_db.scalars().all()
        success = 0
        blocked = 0
        s_message = await callback.message.answer(f'Идет рассылка, ожидайте...')
        for user in users:
            try:
                await bot.copy_message(
                    chat_id=user.telegram_id,
                    from_chat_id=callback.from_user.id,
                    message_id=message_to_send,
                    parse_mode="HTML"
                )
                success += 1
                await asyncio.sleep(0.05)  # Задержка для избежания лимитов
            except Exception as e:
                blocked += 1
                await session.delete(user)
                await asyncio.sleep(0.05)
        await session.commit()
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=s_message.message_id)
    await callback.message.answer(f"📊 Результат рассылки:\n"
                                                 f"✅ Успешно: {success}\n"
                                                 f"❌ Заблокировали: {blocked}", parse_mode="HTML")
    await callback.answer()

@router.message(Command("add_admin"))
async def add_admin(message: types.Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as session:
        record = await session.execute(select(Users.user_role).where(Users.telegram_id==int(user_id)))
        user_role = record.scalar_one_or_none()

    if user_role != 'admin':
        await message.answer(f'❌ Нет прав администратора!\n'
                             f'Попросите администратора дать вам права админа.\n'
                             f'Отправьте ему свой юзернейм', parse_mode='HTML')
        return

    username_to_add = message.text.split()[-1]

    if username_to_add==message.text:
        await message.answer('❌ Нужно отправить команду в формате:\n'
                             '/add_admin @username')
        return

    username_clear = username_to_add.replace('@', '')
    async with AsyncSessionLocal() as admin_session:
        record = await admin_session.execute(select(Users).where(Users.telegram_username==str(username_clear)))
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
                             f'Отправьте ему свой юзернейм', parse_mode='HTML')
        return

    user_to_stat = message.text.split()[-1]
    if user_to_stat==message.text:
        await message.answer('❌ Нужно отправить команду в формате:\n'
                             '/stat @username')
        return

    username_clear = user_to_stat.replace('@', '')
    async with AsyncSessionLocal() as admin_session:
        record = await admin_session.execute(select(Users).where(Users.telegram_username==str(username_clear)))
        user = record.scalar_one_or_none()


        if user is None:
            await message.answer('❌ Пользователя нет в базе данных!\n'
                                 'Пользователю нужно зайти в бота и выбрать язык, тогда он попадет в базу данных')
            return
        id_to_stat = user.telegram_id

        client_username = user.telegram_username
        client_lang = user.user_lang
        client_manager = user.manager_username
        clinet_by_ref = user.ref
        if clinet_by_ref is None:
            user_ref = 'отсутствует'
        else:
            record_ref = await admin_session.execute(select(Users.telegram_username).where(Users.ref==int(clinet_by_ref)))
            user_ref = record_ref.scalar_one_or_none()
            user_ref = f'@{user_ref}'
    async with AsyncSessionLocal() as ref_session:
        record = await ref_session.execute(select(func.count(Users.id)).where(Users.ref==int(id_to_stat)))
        ref_count = record.scalar()
        if ref_count is None:
            ref_count = 0

    await message.answer(f'Статистика по пользователю c ID {id_to_stat}\n\n'
                         f'Юзернейм: @{client_username}\n'
                         f'Выбранный язык: {client_lang}\n'
                         f'Менеджер: @{client_manager}\n'
                         f'Реферал: {user_ref}\n'
                         f'Привлечено лидов: {ref_count}')






