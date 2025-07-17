from keyboards import *
from database import User
from asyncio import sleep
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.methods import AnswerCallbackQuery


router = Router()


@router.callback_query(lambda callback: callback.data == 'account_settings')
async def account_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        '⚙️ Настройки Вашего аккаунта',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f'Показ фактов: {await User(callback.message.chat.id).user_is_allow_see_facts()}'
                        .replace('False', '❌').replace('True', '✅'),
                        callback_data='change_allow_see_facts')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_account')
                ]
            ]
        )
    )

    await sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.callback_query(lambda callback: callback.data == 'change_allow_see_facts')
async def change_account_allow_see_facts(callback: CallbackQuery):
    if await User(callback.message.chat.id).user_is_allow_see_facts() is True:
        text = 'Вы выключили показ фактов'
        boolean = False
    else:
        text = 'Вы включили показ фактов'
        boolean = True

    await User(callback.message.chat.id).change_allow_see_facts(boolean)

    await AnswerCallbackQuery(
        callback_query_id=callback.id,
        show_alert=True,
        text=text
    )

    await account_settings(callback)


@router.callback_query(lambda callback: callback.data == 'back_to_account')
async def back_to_account(callback: CallbackQuery):
    await callback.message.edit_text(
        text=f'👤 <b>{callback.message.chat.full_name}, ваш аккаунт:</b>\n\n'
             f'Показ фактов: {await User(callback.message.chat.id).user_is_allow_see_facts()}'
        .replace('False', '❌').replace('True', '✅'),
        reply_markup=keyboard_account
    )
