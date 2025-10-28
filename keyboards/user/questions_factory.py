from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class QuestionsButtons(CallbackData, prefix="q"):
    button_id: int
    button_text: str  # Сохраняем текст кнопки
    question_id: int

qstns_btns_info = {
    1 : [
        (1, "Facebook", 1),
        (2, "Google", 1),
        (3, "TikTok", 1),
        (4, "Taboola/Outbrain", 1),
        (5, "MGID", 1),
        (6, "Mi Ads", 1),
        (7, "Несколько (нап.)", 1),
        (8, "Другое (нап.)", 1)
    ],
    2 : [
        (1, "Нутра", 2),
        (2, "Крипта", 2),
        (3, "Гембла", 2),
        (4, "Другое (нап.)", 2)
    ],
    3 : [
        (1, "до 100к", 3),
        (2, "100-500к", 3),
        (3, "500к-1кк", 3),
        (4, "> 1кк", 3)
    ],
    4 : [
        (1, "Менее года", 4),
        (2, "1-3 года", 4),
        (3, "3-5 лет", 4),
        (4, "Более 5 лет", 4)
    ],
    5 : [
        (1, "Нативная", 5),
        (2, "Facebook", 5),
        (3, "Google ads", 5),
        (4, "Другое (нап.)", 5)
    ],
    6 : [
        (1, "Работаем", 6),
        (2, "Работали", 6),
        (3, "Не работали", 6)
    ],
    7 : [
        (1, "Тир 1", 7),
        (2, "Тир 2", 7),
        (3, "Тир 3", 7),
        (4, "Другое (нап.)", 7)
    ]
}

qstns_btns_info_en = {
    1 : [
        (1, "Facebook", 1),
        (2, "Google", 1),
        (3, "TikTok", 1),
        (4, "Taboola/Outbrain", 1),
        (5, "MGID", 1),
        (6, "Mi Ads", 1),
        (7, "Multiple (specify)", 1),
        (8, "Other (specify)", 1)
    ],
    2 : [
        (1, "Nutra", 2),
        (2, "Crypto", 2),
        (3, "Gambling", 2),
        (4, "Other (specify)", 2)
    ],
    3 : [
        (1, "Up to $100K", 3),
        (2, "$100K–$500K", 3),
        (3, "$500K–$1M", 3),
        (4, "Over $1M", 3)
    ],
    4 : [
        (1, "< 1 year", 4),
        (2, "1–3 years", 4),
        (3, "3-5 years", 4),
        (4, "Over 5 years", 4)
    ],
    5 : [
        (1, "Native", 5),
        (2, "Facebook", 5),
        (3, "Google Ads", 5),
        (4, "Other (specify)", 5)
    ],
    6 : [
        (1, "Yes, currently work", 6),
        (2, "Yes, worked in a past", 6),
        (3, "No, never worked with", 6)
    ],
    7 : [
        (1, "Tier 1", 7),
        (2, "Tier 2", 7),
        (3, "Tier 3", 7),
        (4, "Other (specify)", 7)
    ]
}

async def get_question_keyboard(question_id, user_lang):
    builder = InlineKeyboardBuilder()
    if user_lang == 'ru':
        btns_info = qstns_btns_info
    else:
        btns_info = qstns_btns_info_en
    for btn_id, text, qstn_id in btns_info[question_id]:
        builder.button(
            text=text,
            callback_data=QuestionsButtons(
                button_id=btn_id,
                button_text=text,
                question_id=qstn_id
            )
        )

    builder.adjust(2)  # 2 кнопки в ряд
    return builder.as_markup()
