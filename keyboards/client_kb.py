from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

b1 = KeyboardButton('Контакты')
b2 = KeyboardButton('Режим работы')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(b1).insert(b2)

kb_menu = ReplyKeyboardMarkup(resize_keyboard=True)
kb_menu.add(
    KeyboardButton('Админ-панель')
)

kb_adm = ReplyKeyboardMarkup(resize_keyboard=True)
kb_adm.add(
    KeyboardButton('✘ Чёрный список'),
    KeyboardButton('✅ Добавить в ЧС'),
    KeyboardButton('❎ Убрать из ЧС')
)
kb_adm.add(KeyboardButton('💬 Рассылка'))
kb_adm.add('⏪ Назад')

kb_back = ReplyKeyboardMarkup(resize_keyboard=True)
kb_back.add(
    KeyboardButton('⏪ Отмена')
)


def fun(user_id):
    quest = InlineKeyboardMarkup(row_width=3)
    quest.add(
        InlineKeyboardButton(text='💬 Ответить', callback_data=f'{user_id}-ans'),
        InlineKeyboardButton(text='❎ Удалить', callback_data='ignor')
    )
    return quest