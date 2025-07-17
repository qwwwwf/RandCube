import string
import random
import asyncio
from keyboards import *
from aiogram import Router
from database import Event
from bots_starting import bot_tg
from dotenv import load_dotenv
from misc.states import GetData
from aiogram.utils.markdown import hlink
from aiogram.fsm.context import FSMContext
from misc.functions import generate_winner
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import CallbackQuery, Message


load_dotenv()
router = Router()


# <--------------- / BACK TO EVENTS / --------------->
@router.callback_query(lambda callback: callback.data == 'back_to_events')
async def back_to_events(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text='<b>Категория:</b> 🏆 Определение победителя\n\n'
             '<b>Описание:</b> тут можно определить победителя по ссылке на пост ВКонтакте, либо принять участие'
             'в розыгрыше в самом боте! 🥇',
        reply_markup=keyboard_events
    )


# <--------------- / VK EVENTS / --------------->
@router.callback_query(lambda callback: callback.data == 'get_winner_vk')
async def get_winner_vk(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetData.post_url)
    await callback.message.edit_text(
        '⭐ <b>Введите ссылку на пост ВКонтакте</b>\n\n'
        'ℹ️ Пост должен существовать и быть в открытой группе',
        reply_markup=keyboard_back_to_events
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.message(GetData.post_url)
async def gwk_state_post_url(message: Message, state: FSMContext):
    response = await generate_winner(message.text)
    await state.clear()

    if len(response) != 0:
        await message.answer(
            f'🏆 Победитель - <b>{response["username"]}!</b>\n'
            f'👤 Ссылка на страницу - {response["user_url"]}'
        )
    else:
        await message.answer(
            '❌ <b>Произошла ошибка при определении победителя</b>\n\n'
            'ℹ️ Возможно Вы отправили ссылку на несуществующий пост, либо он находится в приватной группе',
            reply_markup=keyboard_back_to_events
        )


# <--------------- / BOT EVENTS / --------------->.
@router.callback_query(lambda callback: callback.data == 'enter_in_event')
async def enter_in_event(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetData.event_key)
    await callback.message.edit_text(
        '🔑 <b>Введите код для участия в розыгрыше</b>',
        reply_markup=keyboard_back_to_events
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.message(GetData.event_key)
async def event_state_enter_key(message: Message, state: FSMContext):
    await state.clear()

    if await Event(message.chat.id).add_user_into_event(message.text) is True:
        await message.answer(
            '✅ <b>Вы успешно приняли участие в розыгрыше</b>\n\n'
            'ℹ️ Вы можете следить за статусом розыгрыша:\n<i>Аккаунт → Мои участия</i>'
        )
    else:
        await message.answer(
            '❌ <b>Произошла ошибка при попытке участия</b>\n\n'
            'ℹ️ Возможно Вы уже участвуете в розыгрыше, либо его не существует',
            reply_markup=keyboard_back_to_events
        )


@router.callback_query(lambda callback: callback.data == 'account_my_event')
async def account_my_event(callback: CallbackQuery):
    data = await Event(callback.message.chat.id).get_user_event()

    if len(data) != 0:
        await callback.message.edit_text(
            f'🔑 <b>Код розыгрыша:</b> <code>{data["secret_id"]}</code>\n'
            f'🔗 <b>Ссылка розыгрыша:</b> t.me/RandomizerCube_bot?start={data["secret_id"]}\n\n'
            f'🏆 <b>Призовых мест:</b> {data["prizes_count"]}\n'
            f'👥 <b>Участников:</b> {len(data["members"])}/{data["members_count"]}\n\n'
            f'📜 <b>Описание:</b>\n<i>{data["description"]}</i>',
            reply_markup=keyboard_event_settings
        )
    else:
        await callback.message.edit_text(
            'У вас нет розыгрыша',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text='➕ Создать розыгрыш', callback_data='create_event')
                    ],
                    [
                        InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_account')
                    ]
                ]
            )
        )


@router.callback_query(lambda callback: callback.data == 'cancel_event')
async def cancel_event(callback: CallbackQuery):
    await callback.message.edit_text(
        '❌ <b>Розыгрыш отменен</b>',
        reply_markup=keyboard_back_to_account
    )

    secret_id = (await Event(callback.message.chat.id).get_user_event())['secret_id']
    await Event(callback.message.chat.id).cancel_event(secret_id)
    event_members = await Event(callback.message.chat.id).get_event_members(secret_id)

    for member_id in event_members:
        await bot_tg.send_message(
            chat_id=member_id,
            text=f'❌ <b>Розыгрыш <code>{secret_id}</code> отменен</b>'
        )


@router.callback_query(lambda callback: callback.data == 'create_event')
async def create_event(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetData.event_creation)
    await callback.message.edit_text(
        '⚙️ <b>Введите количество призовых мест и общее количество участников\n</b>'
        'Например: 1 100 (1 призовое место, 100 участников)',
        reply_markup=keyboard_back_to_account
    )


@router.message(GetData.event_creation)
async def event_state_creation(message: Message, state: FSMContext):
    await state.clear()
    split_message = message.text.split()

    if len(split_message) == 2:
        try:
            if int(split_message[0]) >= 1 and int(split_message[1]) >= 2:
                if int(split_message[0]) <= int(split_message[1]):
                    new_secret_id = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
                    await Event(message.chat.id)\
                        .create_event(new_secret_id, int(split_message[0]), int(split_message[1]))

                    await message.reply(
                        '✅ Розыгрыш успешно создан, подробнее о нем можно узнать в аккаунте',
                        reply_markup=keyboard_close
                    )
                else:
                    await message.reply('⚠️ Количество призовых мест должно быть меньше или равно количеству '
                                        'участников')
            else:
                await message.reply('⚠️ Количество призовых мест должно быть больше или равно 1, а также количество '
                                    'участников должно быть больше 1')
        except:
            await message.reply('⚠️ Необходимо написать целые числа')
    else:
        await message.reply('⚠️ Необходимо написать 2 числа')


@router.callback_query(lambda callback: callback.data == 'edit_event_description')
async def edit_event_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GetData.edit_event_description)
    await callback.message.edit_text(
        '⚙️ <b>Введите новое описание для розыгрыша, которое не превышает 200 символов</b>',
        reply_markup=keyboard_back_to_account
    )


@router.message(GetData.edit_event_description)
async def event_state_creation(message: Message, state: FSMContext):
    await state.clear()

    secret_id = (await Event(message.chat.id).get_user_event())['secret_id']

    if len(message.text) <= 200:
        await Event(message.chat.id).update_event_description(secret_id, message.text)
        await message.reply(
            '✅ Вы успешно установили новое описание розыгрыша',
            reply_markup=keyboard_close
        )
    else:
        await message.reply('⚠️ Максимальное количество символов в описании: <b>200</b>')


@router.callback_query(lambda callback: callback.data == 'account_events')
async def account_events(callback: CallbackQuery):
    data = await Event(callback.message.chat.id).get_users_events()

    text = '<i>сейчас нет активных розыгрышей</i>'
    if len(data) != 0:
        user_events = []

        for event in data:
            user_events.append(
                f'🔑 <b>Код:</b> <code>{event[1]}</code>\n'
                f'📜 <b>Описание:</b>\n<i>{event[6]}</i>'
            )

        text = '\n➖\n\n'.join(user_events)

    await callback.message.edit_text(
        f'🎯 <b>Активные розыгрыши с Вашим участием:\n\n</b>{text}',
        reply_markup=keyboard_back_to_account
    )


@router.callback_query(lambda callback: callback.data == 'get_event_winner')
async def get_event_winner(callback: CallbackQuery):
    data = await Event(callback.message.chat.id).get_user_event()

    if len(data) != 0:
        if len(data['members']) != 0:
            if data['prizes_count'] >= len(data['members']):
                winners = random.choices(data['members'], k=len(data['members']))
            else:
                winners = random.choices(data['members'], k=data['prizes_count'])

            text = '🎊 <b>Победители розыгрыша:\n\n</b>' +\
                   '\n'.join([f'<b>{i + 1}.</b> {hlink((await bot_tg.get_chat(winners[i])).first_name, f"tg://user?id={winners[i]}")}'
                              for i in range(len(winners))])

            for member_id in data['members']:
                place_in_the_top = ''
                if member_id in winners:
                    place_in_the_top = f'🏆 Вы заняли <b>#{winners.index(member_id) + 1}</b> место\n'

                await bot_tg.send_message(
                    chat_id=member_id,
                    text=f'🎉 <b>Розыгрыш <code>{data["secret_id"]}</code> завершился!</b>\n'
                         f'{place_in_the_top}\n➖➖➖➖➖\n<b>Итоги</b>\n➖➖➖➖➖\n\n{text}'
                )

            await callback.message.edit_text(
                text,
                reply_markup=keyboard_close
            )

            await Event(callback.message.chat.id).cancel_event(data['secret_id'])
            await Event(callback.message.chat.id).update_event_winners(data['secret_id'], winners)
        else:
            await AnswerCallbackQuery(
                callback_query_id=callback.id,
                show_alert=True,
                text=f'⚠️ В розыгрыше пока нет участников'
            )
    else:
        await callback.message.delete()
