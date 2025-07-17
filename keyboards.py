import configparser
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


config = configparser.ConfigParser()
config.read('config.ini')


keyboard_main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🎲 Генерация'),
            KeyboardButton(text='🏆 Определение победителя')
        ],
        [
            KeyboardButton(text='👤 Аккаунт'),
        ],
        [
            KeyboardButton(text='☎️ Обратная связь'),
            KeyboardButton(text='ℹ️ О боте')
        ]
    ],
    resize_keyboard=True
)

keyboard_generation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🔢 Случайное число', callback_data='random_number'),
            InlineKeyboardButton(text='🔑 Случайный пароль', callback_data='random_password')
        ],
        [
            InlineKeyboardButton(text='📃 Случайная запись', callback_data='random_string'),
            InlineKeyboardButton(text='🃏 Случайная карта', callback_data='random_playing_card'),
        ],
        [
            InlineKeyboardButton(text='🎲 Бросить кубик', callback_data='dice'),
            InlineKeyboardButton(text='🪙 Бросить монетку', callback_data='coinflip')
        ],
        [
            InlineKeyboardButton(text='🎱 Шар 8', callback_data='8ball'),
            InlineKeyboardButton(text='🎫 Счастливый билет', callback_data='random_ticket')
        ],
        [
            InlineKeyboardButton(text='🔮 Случайный факт', callback_data='random_fact')
        ]
    ]
)

keyboard_events = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🎲 Определить победителя (ВК)', callback_data='get_winner_vk')
        ],
        [
            InlineKeyboardButton(text='🔑 Ввести код розыгрыша', callback_data='enter_in_event')
        ]
    ]
)

keyboard_feedback = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='✉️ Написать', url=f't.me/{config["Contacts"]["support_url"]}')
        ],
        [
            InlineKeyboardButton(text='Оставить отзыв', url='https://forms.gle/QQZwFVbQLow7a1gA9')
        ]
    ]
)

keyboard_account = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='⚙️ Настройки', callback_data='account_settings')
        ],
        [
            InlineKeyboardButton(text='🎁 Мой розыгрыш', callback_data='account_my_event'),
            InlineKeyboardButton(text='🎯 Мои участия', callback_data='account_events')
        ]
    ]
)

keyboard_event_settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🎲 Подвести итог', callback_data='get_event_winner')
        ],
        [
            InlineKeyboardButton(text='📜 Изменить описание', callback_data='edit_event_description')
        ],
        [
            InlineKeyboardButton(text='❌ Отменить розыгрыш', callback_data='cancel_event')
        ],
        [
            InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_account')
        ]
    ]
)

keyboard_back_to_gen_commands = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_generation_commands')
        ]
    ]
)

keyboard_back_to_events = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_events')
        ]
    ]
)

keyboard_back_to_account = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_account')
        ]
    ]
)

keyboard_close = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Закрыть', callback_data='close')
        ]
    ]
)
