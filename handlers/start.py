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
from keyboards.user.questions_factory import QuestionsButtons
from keyboards.user.ref_user_menu import ref_back_ru, ref_menu_ru, ref_menu_en, ref_back_en

from database.database import AsyncSessionLocal
from database.models import Users
from keyboards.main_menu_builder import main_menu_builder
from keyboards.user.start_menu_lang import start_menu_lang

router = Router(name='start_router')

@router.message(CommandStart(deep_link=True))
@router.message(Command('start'))
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

    try:
        payload = decode_payload(command.args) if command.args else None
    except:
        payload = None

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
        sent_message = await message.answer('🚀 С нами реклама льется без блоков и реджектов. LuxBot поможет арендовать акки под любые источники и гео — быстро и без рисков.\n\n'
                                            'Мы берём на себя всю операционку, чтобы вы сосредоточились на трафике и профите 💸\n\n'
                                            'Выберите язык ⬇️', reply_markup=start_menu_lang, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)
    else:
        sent_message = await message.answer('🚀 With us, advertising flows without blocks and rejects. LuxBot helps rent accounts for any traffic sources and GEOs — quickly and without risks.\n\n'
                                            'We handle all the operational work so you can focus on traffic and profit 💸\n\n'
                                            'Choose your language ⬇️', reply_markup=start_menu_lang, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)

@router.callback_query(QuestionsButtons.filter((F.button_text == 'Назад в меню') | (F.button_text == 'Back to menu')))
@router.callback_query(F.data=='main_menu')
async def start_menu(event: Union[types.Message, types.CallbackQuery], state: FSMContext):
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
        await callback.message.delete()

    data = await state.get_data()
    if data:
        try:
            user_ref = data.get('user_ref')
            if user_ref:
                await state.clear()
                await state.update_data(user_ref=user_ref)
        except:
            await state.clear()
            pass


    if user_lang == 'ru':
        sent_message = await message.answer('🚀 С нами реклама льется без блоков и реджектов. LuxBot поможет арендовать акки под любые источники и гео — быстро и без рисков.\n\n'
                                            'Мы берём на себя всю операционку, чтобы вы сосредоточились на трафике и профите 💸\n\n'
                                            'Выберите язык ⬇️', reply_markup=start_menu_lang, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)
    else:
        sent_message = await message.answer('🚀 With us, advertising flows without blocks and rejects. LuxBot helps rent accounts for any traffic sources and GEOs — quickly and without risks.\n\n'
                                            'We handle all the operational work so you can focus on traffic and profit 💸\n\n'
                                            'Choose your language ⬇️', reply_markup=start_menu_lang, parse_mode="HTML")
        await state.update_data(sent_message_id=sent_message.message_id)

@router.message(Command("ref"))
@router.callback_query(F.data=='ref')
async def referal(event: Union[types.Message, types.CallbackQuery]):

    if isinstance(event, types.Message):
        message = event
        user_id = message.from_user.id
    else:
        callback = event
        message = callback.message
        user_id = callback.from_user.id
        await callback.answer()
        await callback.message.delete()


    async with AsyncSessionLocal() as session:
        record = await session.execute(select(func.count(Users.id)).where(Users.ref==int(user_id)))
        refs_count = record.scalar()
        if refs_count is None:
            refs_count = 0

        record_lang = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = record_lang.scalar_one_or_none()

    if user_lang == 'ru':
        # text_message = (f'Приветствуем в реферальной программе Luxaccs!\n'
        #                  f'Если по вашей ссылке придет 10 активно работающих с нами клиентов, то вы получаете персональную скидку в 5%\n'
        #                  f'Вот ваша ссылка: <code>{user_ref_url}</code> (копируется при нажатии)\n'
        #                  f'Привлечено активных клиентов: {refs_count}')
        text_message = (f'Наша реферальная программа действует для следующих источников трафика: Facebook, MGID, Google Ads, Bing, Bigo, Taboola, DV360 и TikTok. Рефер получает выплаты за каждого приведенного клиента, который закажет у нас аккаунты и покажет спенд, выплату можно потратить на account fee (наш клиент), или же вывести себе на кошелек (50% указанной суммы, если не является нашим клиентом).\n\n'
                        f'Привлечено активных клиентов: {refs_count}')
        keyboard = ref_menu_ru
    else:
        # text_message = (f'Welcome to the Luxaccs referral program!\n'
        #                  f'If 10 active clients who work with us come through your link, you will receive a personal 5% discount.\n'
        #                  f'Here is your link: <code>{user_ref_url}</code> (tap to copy)\n'
        #                  f'Active clients referred:: {refs_count}')
        text_message = (f"Our referral program applies to the following traffic sources: Facebook, MGID, Google Ads, Bing, Bigo, Taboola, DV360, and TikTok. The referrer receives a payment for each referred customer who orders accounts from us and demonstrates spend. The payment can be used for account fees (for our customer) or withdrawn to the referrer's own wallet (50% of the specified amount if they are not our customer).\n\n"
                        f"Active clients referred: {refs_count}")
        keyboard = ref_menu_en
    await message.answer(text_message, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data=='ref_info')
async def referal_info(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        record_lang = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = record_lang.scalar_one_or_none()

    if user_lang == 'ru':
        text_message = (f'- Требования к рефералу (KPI): Заказ аккаунтов и оплата. Проявление активности и работа с нами минимум неделя\n\n'
                        f'- Награды для реферера: Покрытие account fee (наши клиенты), либо выплата 50% на кошелек (сторонние люди, цифры в соответствующих разделах меню)')
        keyboard = ref_back_ru
    else:
        text_message = (f'- Referral requirements (KPI): Ordering accounts and paying. Showing activity and working with us for at least a week.\n\n'
                        f'- Rewards for the referrer: Coverage of account fee (our customers), or a 50% payout to a wallet (for third parties, figures in the corresponding menu sections).')
        keyboard = ref_back_en
    await callback.message.answer(text_message, reply_markup=keyboard, parse_mode='HTML')

@router.callback_query(F.data=='ref_fb')
async def referal_fb(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        record_lang = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = record_lang.scalar_one_or_none()

    if user_lang == 'ru':
        text_message = (f'Для Facebook действует процентное вознаграждение:\n\n'
                        f'● 0,5% от спенда реферального клиента\n'
                        f'● Срок выплат: первые 3 месяца с момента старта работы реферала\n'
                        f'● Формат выплат:\n'
                        f'  • каждые 2 недели\n'
                        f'  • одним платежом по завершении 3-месячного периода (на выбор)')
        keyboard = ref_back_ru
    else:
        text_message = (f"For Facebook, a percentage-based reward applies:\n\n"
                        f"● 0.5% of the referral client's spend\n"
                        f"● Payout period: the first 3 months from the start of the referral's work\n"
                        f"● Payout format:\n"
                        f"  • every 2 weeks\n"
                        f"  • in a single payment upon completion of the 3-month period (to choose from)")
        keyboard = ref_back_en
    await callback.message.answer(text_message, reply_markup=keyboard, parse_mode='HTML')

@router.callback_query(F.data=='ref_other')
async def referal_other(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        record_lang = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = record_lang.scalar_one_or_none()

    if user_lang == 'ru':
        text_message = (f'Для остальных источников действует фиксированная реферальная выплата, зависящая от того, является ли реферер нашим действующим клиентом.\n\n'
                        f'Первая цифра — если человек работает с нами (на покрытие account fee).\n'
                        f'Вторая цифра — если не работает, но приводит нам клиента (выплату получает на кошелек).\n\n'
                        f'● MGID: 50 USD / 25 USD\n' 
                        f'● Google Ads: 35 USD / 25 USD\n'
                        f'● Bing: 50 USD / 25 USD\n'
                        f'● Bigo: 50 USD / 25 USD\n'
                        f'● Taboola: 200 USD / 100 USD\n' 
                        f'● DV360: 350 USD / 175 USD\n' 
                        f'● TikTok: 50 USD / 25 USD\n\n'
                        f'Вся статистика рефералов и статусы доступны рефереру по таблице. Всё честно: выплаты только по проверенным результатам.')
        keyboard = ref_back_ru
    else:
        text_message = (f"For other sources, a fixed referral payment applies, depending on whether the referrer is an existing client of ours.\n\n"
                        f"The first figure is if the person works with us (to cover the account fee).\n"
                        f"The second figure is if they do not work with us but refer a client to us (the payment is received to their wallet).\n\n"
                        f"● MGID: 50 USD / 25 USD\n" 
                        f"● Google Ads: 35 USD / 25 USD\n"
                        f"● Bing: 50 USD / 25 USD\n"
                        f"● Bigo: 50 USD / 25 USD\n"
                        f"● Taboola: 200 USD / 100 USD\n" 
                        f"● DV360: 350 USD / 175 USD\n" 
                        f"● TikTok: 50 USD / 25 USD\n\n"
                        f"All referral statistics and statuses are available to the referrer via the table. Everything is fair: payments are only made for verified results.")
        keyboard = ref_back_en
    await callback.message.answer(text_message, reply_markup=keyboard, parse_mode='HTML')

@router.callback_query(F.data=='ref_link')
async def referal_link(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.delete()

    async with AsyncSessionLocal() as session:
        record = await session.execute(select(func.count(Users.id)).where(Users.ref==int(user_id)))
        refs_count = record.scalar()
        if refs_count is None:
            refs_count = 0

        record_lang = await session.execute(select(Users.user_lang).where(Users.telegram_id==int(user_id)))
        user_lang = record_lang.scalar_one_or_none()
    user_ref_url = await create_start_link(bot, payload=str(user_id), encode=True)

    if user_lang == 'ru':
        text_message = (f'Вот ваша ссылка: <code>{user_ref_url}</code> (копируется при нажатии)\n\n'
                        f'Привлечено активных клиентов: {refs_count}')
        keyboard = ref_back_ru
    else:
        text_message = (f"Here is your link: <code>{user_ref_url}</code> (tap to copy)\n\n"
                        f"Active clients referred: {refs_count}")
        keyboard = ref_back_en
    await callback.message.answer(text_message, reply_markup=keyboard, parse_mode='HTML')