from aiogram import types, Router, F
from aiogram.filters import Command
from typing import Union
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from config.bot_config import bot, CHAT_ID
from sqlalchemy import select, and_, func, or_, text
from .google_sheets import add_record_to_sheet
from datetime import datetime

from database.database import AsyncSessionLocal
from database.models import Users
from keyboards.user.questions_factory import QuestionsButtons, get_question_keyboard
from handlers.new_topic import create_user_topic

router = Router(name='questions_router')

class Questions(StatesGroup):
    question_1 = State()
    question_4 = State()
    question_2 = State()
    # question_7 = State()
    # question_8 = State()

@router.callback_query(F.data=='ru')
async def ru_start_menu(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_fullname = str(callback.from_user.full_name)
    user_username = str(callback.from_user.username)
    chat_id = callback.message.chat.id

    await callback.answer()
    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        user_db = await session.execute((select(Users).where(Users.telegram_id == user_id)))
        user_data = user_db.scalar_one_or_none()
        if user_data is None:
            new_user = Users(
                telegram_id=int(user_id),
                telegram_username=user_username,
                full_name=user_fullname,
                user_lang='ru',

            )
            session.add(new_user)
            await session.commit()
        keyboard = await get_question_keyboard(1, 'ru')
        sent_message = await callback.message.answer('1) Ваши основные источники трафика?', reply_markup=keyboard, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)

@router.callback_query(F.data=='en')
async def en_start_menu(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_fullname = str(callback.from_user.full_name)
    user_username = str(callback.from_user.username)
    chat_id = callback.message.chat.id

    await callback.answer()
    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        user_db = await session.execute((select(Users).where(Users.telegram_id == user_id)))
        user_data = user_db.scalar_one_or_none()
        if user_data is None:
            new_user = Users(
                telegram_id=int(user_id),
                telegram_username=user_username,
                full_name=user_fullname,
                user_lang='en',

            )
            session.add(new_user)
            await session.commit()
        keyboard = await get_question_keyboard(1, 'en')
        sent_message = await callback.message.answer('1) Your main traffic sources?', reply_markup=keyboard, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)

@router.callback_query(QuestionsButtons.filter((F.button_text == 'Другое (нап.)') | (F.button_text == 'Несколько (нап.)') | (F.button_text == 'Other (specify)') | (F.button_text == 'Multiple (specify)')))
async def other_questions_manual(callback: types.CallbackQuery, callback_data: QuestionsButtons, state: FSMContext):
    user_id = callback.from_user.id
    async with AsyncSessionLocal() as session:
        user_data = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = user_data.scalar_one_or_none()

    question_id = callback_data.question_id
    if question_id==1:
        st=Questions.question_1
    elif question_id==2:
        st=Questions.question_2
    # elif question_id==6:
    #     st=Questions.question_6
    # elif question_id==7:
    #     st=Questions.question_7
    else:
        await callback.message.answer('Ошибка! Обратитесь к разработчику')
        return

    if user_lang == 'ru':
        message_text = questions_texts_ru[question_id]+f'\nНапишите ответ:'
    else:
        message_text = questions_texts_en[question_id]+f'\nWrite an answer:'



    await callback.answer()
    await callback.message.delete()

    sent_message = await callback.message.answer(message_text)
    await state.update_data(sent_message=sent_message.message_id)
    await state.set_state(st)

@router.message(StateFilter(Questions.question_4))
async def last_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    user_name = message.text
    await state.update_data(**{str(4): user_name})

    data = await state.get_data()
    await bot.delete_message(user_id, data['sent_message'])
    try:
        user_ref = int(data['user_ref'])
    except:
        user_ref = None
        pass
    async with AsyncSessionLocal() as first_session:
        user_data = await first_session.execute(select(Users).where(Users.telegram_id==int(user_id)))
        user = user_data.scalar_one_or_none()
        user_lang = user.user_lang
        if user_ref:
            user.ref = user_ref
            await first_session.commit()

    await state.clear()
    message_text = ''
    if user_lang == 'ru':
        answer_text = ('✅ Мы получили ваше обращение и ответим в ближайшее время здесь же - в боте. Благодарим за обращение!\n\n'
                       'Так же у нас есть реф программа, о которой вы можете узнать лучше благодаря команде /ref')
        questions = questions_texts_ru
    else:
        answer_text = ("✅ We have received your request and will respond as soon as possible right here in the chat. Thank you for contacting us!\n\n"
                       "We also have a referral program, which you can learn more about using the /ref command.")
        questions = questions_texts_en
    for i in list(range(1, 5)):
        message_text += questions[i]+'\n'
        message_text += (data[str(i)])+'\n'

    async with AsyncSessionLocal() as session:
        db_data = await session.execute(select(Users.thread_id).where(Users.telegram_id==int(user_id)))
        user_topic_id = db_data.scalar_one_or_none()
    await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=user_topic_id,
            text=f'Ответы на опрос:\n\n'
                 f'{message_text}'
    )

    await message.answer(text=answer_text)

    current_time = datetime.now()
    formatted_time = current_time.strftime("%d.%m.%y %H:%M")
    chat_id_for_link = str(CHAT_ID)[4:]
    values_for_sheet = [
        user_id,
        f'@{user_username}',
        formatted_time,
        ' ',
        message_text,
        'Нет',
        f'https://t.me/c/{chat_id_for_link}/{user_topic_id}'

    ]
    await add_record_to_sheet(
        spreadsheet_name='Luxaccs Лиды',
        worksheet_name='Общий',
        values=values_for_sheet
    )

@router.message(StateFilter(Questions))
async def other_questions_state_manual(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    async with AsyncSessionLocal() as session:
        user_data = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = user_data.scalar_one_or_none()
    current_state = await state.get_state()
    question_id = int(current_state.split('_')[-1])

    if question_id==1:
        await create_user_topic(
            bot=bot,
            chat_id=CHAT_ID,
            user_id=user_id,
            user_tg_name=user_username,
            user_lang=user_lang,
            topic_name=f'Лид | {user_username}'
        )

    data = await state.get_data()
    await bot.delete_message(user_id, data['sent_message'])

    next_question_id = question_id+1
    user_answer = message.text

    await state.update_data(**{str(question_id): user_answer})
    if user_lang == 'ru':
        message_text = questions_texts_ru[next_question_id]
    else:
        message_text = questions_texts_en[next_question_id]

    if next_question_id==4:
        sent_message = await message.answer(message_text)
        await state.update_data(sent_message=sent_message.message_id)
        await state.set_state(Questions.question_4)
        return

    keyboard = await get_question_keyboard(next_question_id, user_lang)

    sent_message = await message.answer(message_text, reply_markup=keyboard)
    await state.update_data(sent_message=sent_message.message_id)

@router.callback_query(QuestionsButtons.filter())
async def other_questions(callback: types.CallbackQuery, callback_data: QuestionsButtons, state: FSMContext):
    user_id = callback.from_user.id
    user_username = callback.from_user.username
    async with AsyncSessionLocal() as session:
        user_data = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = user_data.scalar_one_or_none()

    question_id = callback_data.question_id
    next_question_id = question_id+1
    user_answer = callback_data.button_text

    if question_id==1:
        await create_user_topic(
            bot=bot,
            chat_id=CHAT_ID,
            user_id=user_id,
            user_tg_name=user_username,
            user_lang=user_lang,
            topic_name=f'Лид | {user_username}'
        )

    await state.update_data(**{str(question_id): user_answer})
    if user_lang == 'ru':
        message_text = questions_texts_ru[next_question_id]
    else:
        message_text = questions_texts_en[next_question_id]

    if next_question_id==4:
        sent_message = await callback.message.answer(message_text)
        await state.update_data(sent_message=sent_message.message_id)
        await state.set_state(Questions.question_4)
        await callback.answer()
        await callback.message.delete()
        return

    keyboard = await get_question_keyboard(next_question_id, user_lang)

    await callback.answer()
    await callback.message.delete()

    sent_message = await callback.message.answer(message_text, reply_markup=keyboard)
    await state.update_data(sent_message=sent_message.message_id)


questions_texts_ru = {
    1: '1) Ваши основные источники трафика?',
    2: '2) Ваша основная вертикаль?',
    3: '3) Какой у вас ежемесячный спенд?',
    4: '4) Как к вам обращаться?'
    # 5: '5) Какую рекламу льёте?',
    # 6: '6) Работали ли с агентствами по предоставлению рекламных аккаунтов?',
    # 7: '7) На какие гео вы чаще всего льёте рекламу?',
    # 8: '8) Как давно вы в арбитраже?'
}

questions_texts_en = {
    1: '1) Your main traffic sources?',
    2: '2) What is your main vertical?',
    3: '3) What is your monthly spend?',
    4: '4) How should we call you?'
    # 5: '5) What kind of ads do you run??',
    # 6: '6) Have you worked with agencies providing advertising accounts?',
    # 7: '7) Which GEOs do you target most often?',
    # 8: '8) How long have you been in affiliate marketing?'
}