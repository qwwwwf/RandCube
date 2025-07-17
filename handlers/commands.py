from keyboards import *
from aiogram import Router
from database import User, Event
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Text, Command, CommandObject


router = Router()


# <----------/ Commands /---------->

@router.message(Command(commands=['start']))
async def start_command(message: Message, command: CommandObject):
    await message.answer('Добро пожаловать! Вы в меню', reply_markup=keyboard_main)

    if await User(message.chat.id).user_exists() is False:
        await User(message.chat.id).create_user()

    if await Event(message.chat.id).add_user_into_event(command.args) is True:
        await message.answer(
            '✅ <b>Вы успешно приняли участие в розыгрыше</b>\n\n'
            'ℹ️ Вы можете следить за статусом розыгрыша:\n<i>Аккаунт → Мои участия</i>'
        )


@router.message(Text('🎲 Генерация'))
async def category_generation(message: Message):
    await message.answer(
        text='<b>Категория:</b> 🎲 Генерация\n\n'
             '<b>Описание:</b> в этом разделе много случайностей! 😉',
        reply_markup=keyboard_generation
    )


@router.message(Text('🏆 Определение победителя'))
async def category_events(message: Message):
    await message.answer(
        text='<b>Категория:</b> 🏆 Определение победителя\n\n'
             '<b>Описание:</b> тут можно определить победителя по ссылке на пост ВКонтакте, либо принять участие '
             'в розыгрыше в самом боте! 🥇',
        reply_markup=keyboard_events
    )


@router.message(Text('☎️ Обратная связь'))
async def category_feedback(message: Message):
    await message.answer(
        text='<b>Категория:</b> ☎️ Обратная связь\n\n'
             '<b>Описание:</b> если у вас появились вопросы или идеи по улучшению бота, то Вы можете обратиться к нам',
        reply_markup=keyboard_feedback
    )


@router.message(Text('ℹ️ О боте'))
async def category_faq(message: Message):
    await message.answer(
        'Советуем прочитать статью про нашего бота:\n'
        'https://telegra.ph/Randomizer-Bot---luchshij-bot-randomajzer-05-15',
        reply_markup=keyboard_close
    )


@router.message(Text('👤 Аккаунт'))
async def category_account(message: Message):
    await message.answer(
        text=f'👤 <b>{message.chat.full_name}, ваш аккаунт:</b>\n\n'
             f'Показ фактов: {await User(message.chat.id).user_is_allow_see_facts()}'
        .replace('False', '❌').replace('True', '✅'),
        reply_markup=keyboard_account
    )


@router.callback_query(lambda callback: callback.data == 'close')
async def close_message(callback: CallbackQuery):
    await callback.message.delete()
