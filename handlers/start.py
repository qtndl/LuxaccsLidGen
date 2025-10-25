from aiogram import types, Router, F
from aiogram.filters.command import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.filters import Command
from typing import Union
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload
from config.bot_config import bot
from sqlalchemy import select, and_, func, or_, text

from database.database import AsyncSessionLocal
from database.models import Users
from keyboards.main_menu_builder import main_menu_builder
from keyboards.user.start_menu_lang import start_menu_lang

router = Router(name='start_router')

@router.message(CommandStart(deep_link=True))
@router.message(Command('start'))
@router.callback_query(F.data=='main_menu')
async def start_menu(event: Union[types.Message, types.CallbackQuery], state: FSMContext, command: CommandObject):
    callback = None
    if isinstance(event, types.Message):
        message = event
        user_id = message.from_user.id
        user_fullname = str(message.from_user.full_name)
        user_username = str(message.from_user.username)
        user_lang = str(message.from_user.language_code)
        chat_id = message.chat.id
    else:
        callback = event
        message = callback.message
        user_id = callback.from_user.id
        user_fullname = str(callback.from_user.full_name)
        user_username = str(callback.from_user.username)
        user_lang = str(callback.from_user.language_code)
        chat_id = callback.message.chat.id
        await callback.answer()

    payload = decode_payload(command.args) if command.args else None

    data = await state.get_data()
    if data:
        try:
            user_ref = data['user_ref']
            if user_ref:
                await state.clear()
                await state.update_data(user_ref=payload)
        except:
            await state.clear()
            pass

    if payload:
        await state.update_data(user_ref=payload)


    if user_lang == 'ru':
        sent_message = await message.answer('Привет 👋\n'
                                            'Я LuxBot — помогаю выдавать аккаунты для рекламы без блоков и ограничений.\n'
                                            'Выберите язык 👇', reply_markup=start_menu_lang, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)
    else:
        sent_message = await message.answer('Hello 👋\n'
                                            'I am LuxBot — I help provide accounts for advertising without blocks or restrictions.\n'
                                            'Choose a language 👇', reply_markup=start_menu_lang, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)


@router.message(Command("ref"))
async def referal(message: types.Message):
    user_id = message.from_user.id
    user_ref_url = await create_start_link(bot, payload=str(user_id), encode=True)

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(func.count(Users.id)).where(Users.ref==int(user_id)))
        refs_count = record.scalar()
        if refs_count is None:
            refs_count = 0

        record_lang = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = record_lang.scalar_one_or_none()

    if user_lang == 'ru':
        text_message = (f'Приветствуем в реферальной программе Luxaccs!\n'
                         f'Если по вашей ссылке придет 10 активно работающих с нами клиентов, то вы получаете персональную скидку в 5%\n'
                         f'Вот ваша ссылка: <code>{user_ref_url}</code> (копируется при нажатии)\n'
                         f'Привлечено активных клиентов: {refs_count}')
    else:
        text_message = (f'Welcome to the Luxaccs referral program!\n'
                         f'If 10 active clients who work with us come through your link, you will receive a personal 5% discount.\n'
                         f'Here is your link: <code>{user_ref_url}</code> (tap to copy)\n'
                         f'Active clients referred:: {refs_count}')

    await message.answer(text_message, parse_mode='HTML')
