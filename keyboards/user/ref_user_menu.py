from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.button(text='Требования и награды', callback_data=f'ref_info')
builder.button(text='Facebook', callback_data=f'ref_fb')
builder.button(text='Другие источники', callback_data=f'ref_other')
builder.button(text='Получить реф ссылку', callback_data=f'ref_link')

builder.adjust(1)

ref_menu_ru = builder.as_markup()




builder1 = InlineKeyboardBuilder()
builder1.button(text='Назад в меню', callback_data=f'ref')

builder1.adjust(1)

ref_back_ru = builder1.as_markup()




builder2 = InlineKeyboardBuilder()
builder2.button(text='Requirements and rewards', callback_data=f'ref_info')
builder2.button(text='Facebook', callback_data=f'ref_fb')
builder2.button(text='Other sources', callback_data=f'ref_other')
builder2.button(text='Get ref link', callback_data=f'ref_link')

builder2.adjust(1)

ref_menu_en = builder2.as_markup()




builder3 = InlineKeyboardBuilder()
builder3.button(text='Back to menu', callback_data=f'ref')

builder3.adjust(1)

ref_back_en = builder3.as_markup()