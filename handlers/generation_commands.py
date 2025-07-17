import string
import random
import asyncio
from keyboards import *
from database import User
from aiogram import Router
from aiogram.fsm.context import FSMContext
from misc.states import ChangeParams, GetData
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import CallbackQuery, Message
from misc.functions import get_random_string, generate_fact


min_password_size = int(config['Values']['min_password_size'])
max_password_size = int(config['Values']['max_password_size'])
min_value_generation_value = int(config['Values']['min_value_generation_value'])
max_value_generation_value = int(config['Values']['max_value_generation_value'])


with open('handlers/stickers_ids_playingcards.txt', 'r', encoding='utf-8') as file:
    stickers_ids_playingcards = file.read().splitlines()


with open('handlers/stickers_ids_8ball.txt', 'r', encoding='utf-8') as file:
    stickers_ids_8ball = file.read().splitlines()


router = Router()


@router.callback_query(lambda callback: callback.data == 'back_to_generation_commands')
async def category_generation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=f'<b>Категория:</b> 🎲 Генерация\n\n'
             f'<b>Описание:</b> в этом разделе много случайностей! 😉',
        reply_markup=keyboard_generation
    )


# <--------------- / DICE / --------------->
@router.callback_query(lambda callback: callback.data == 'dice')
async def dice(callback: CallbackQuery):
    result = await callback.message.answer_dice('🎲')

    await callback.message.answer(f'Выпало: <b>{result.dice.value}</b>')

    await asyncio.sleep(0.4)
    await AnswerCallbackQuery(callback_query_id=callback.id)


# <--------------- / COINFLIP / --------------->
@router.callback_query(lambda callback: callback.data == 'coinflip')
async def coinflip(callback: CallbackQuery):
    result = random.choice(['орёл', 'решка'])
    await callback.message.answer('🪙')
    await callback.message.answer(f'Выпал <b>{result}</b>' if result == 'орёл' else f'Выпала <b>{result}</b>')

    await asyncio.sleep(0.4)
    await AnswerCallbackQuery(callback_query_id=callback.id)


# <--------------- / RANDOM PLAYING CARD / --------------->
@router.callback_query(lambda callback: callback.data == 'random_playing_card')
async def random_playing_card(callback: CallbackQuery):
    stickers = stickers_ids_playingcards

    await callback.message.answer_sticker(sticker=random.choice(stickers))

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


# <--------------- / RANDOM TICKET / --------------->
@router.callback_query(lambda callback: callback.data == 'random_ticket')
async def random_ticket(callback: CallbackQuery):
    ticket_number = random.randint(000000, 999999)

    result = 'удачным! 🍀' if sum(map(int, list(str(ticket_number)[:3]))) == sum(
        map(int, list(str(ticket_number)[3:]))) else 'неудачным!'

    await callback.message.edit_text(
        f'🎫 Ваш билет: <b>{ticket_number}</b>\nОказался <b>{result}</b>',
        reply_markup=keyboard_back_to_gen_commands
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


# <--------------- / 8BALL / --------------->
@router.callback_query(lambda callback: callback.data == '8ball')
async def random_magic_ball(callback: CallbackQuery):
    stickers = stickers_ids_8ball

    await callback.message.answer_sticker(sticker=random.choice(stickers))

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


# <--------------- / RANDOM FACT / --------------->
@router.callback_query(lambda callback: callback.data == 'random_fact')
async def random_fact(callback: CallbackQuery):
    if await User(callback.message.chat.id).user_is_allow_see_facts() is True:
        await callback.message.edit_text(
            f'🔮 <b>Факт:</b>\n\n{await generate_fact()}',
            reply_markup=keyboard_back_to_gen_commands
        )

        await asyncio.sleep(0.25)
        await AnswerCallbackQuery(callback_query_id=callback.id)
    else:
        await AnswerCallbackQuery(
            callback_query_id=callback.id,
            show_alert=True,
            text='⚠️ Некоторые факты могут быть сомнительного содержания\n\n'
                 'У вас отключен показ фактов, его можно включить в настройках аккаунта:\n\n'
                 '👤 Аккаунт → ⚙️ Настройки'
        )


# <--------------- RANDOM NUMBER --------------->
@router.callback_query(lambda callback: callback.data == 'random_number')
async def random_number(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_number()

    await callback.message.edit_text(
        '🔢 <b>Случайное число</b>\n\n'
        f'🔁 Кол-во генераций: <b>{last_data["generation_count"]}</b>\n'
        f'📏 Диапазон: от <b>{last_data["min_value"]}</b> до <b>{last_data["max_value"]}</b>',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='-', callback_data='minus_generation_number_counter'),
                    InlineKeyboardButton(text=last_data["generation_count"],
                                         callback_data='change_generation_number_counter'),
                    InlineKeyboardButton(text='+', callback_data='plus_generation_number_counter')
                ],
                [
                    InlineKeyboardButton(text='🎲 Сгенерировать', callback_data='generate_number')
                ],
                [
                    InlineKeyboardButton(text='⚙️ Изменить диапазон', callback_data='change_generate_number_params')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_generation_commands')
                ]
            ]
        )
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.callback_query(lambda callback: callback.data == 'generate_number')
async def generate_number(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_number()

    result = []
    for _ in range(last_data['generation_count']):
        result.append(str(random.randint(last_data['min_value'], last_data['max_value'])))

    await callback.message.edit_text(
        ';  '.join(result),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='random_number')
                ]
            ]
        )
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.callback_query(lambda callback: callback.data == 'minus_generation_number_counter')
async def minus_generation_number_counter(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_number()

    if last_data['generation_count'] > min_value_generation_value:
        last_data['generation_count'] -= 1
        await User(callback.message.chat.id).update_generation_number_params(last_data)
        await random_number(callback)
    else:
        await AnswerCallbackQuery(
            callback_query_id=callback.id,
            show_alert=True,
            text=f'⚠️ Минимальное допустимое количество генераций: {min_value_generation_value}'
        )


@router.callback_query(lambda callback: callback.data == 'plus_generation_number_counter')
async def plus_generation_number_counter(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_number()

    if last_data['generation_count'] <= max_value_generation_value:
        last_data['generation_count'] += 1
        await User(callback.message.chat.id).update_generation_number_params(last_data)
        await random_number(callback)
    else:
        await AnswerCallbackQuery(
            callback_query_id=callback.id,
            show_alert=True,
            text=f'⚠️ Максимальное допустимое количество генераций: {max_value_generation_value}'
        )


@router.callback_query(lambda callback: callback.data == 'change_generation_number_counter')
async def change_generation_number_counter(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f'⚙️ <b>Введите количество генераций (от {min_value_generation_value} до {max_value_generation_value})</b>',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_gen_command_number')
                ]
            ]
        )
    )
    await state.set_state(ChangeParams.generation_count_number)


@router.message(ChangeParams.generation_count_number)
async def change_params_generation_number_count(message: Message, state: FSMContext):
    await state.clear()
    if message.text.isnumeric():
        if min_value_generation_value <= int(message.text) <= max_value_generation_value:
            last_data = await User(message.chat.id).get_last_generation_number()

            last_data['generation_count'] = int(message.text)

            await User(message.chat.id).update_generation_number_params(last_data)
            await message.reply(
                f'✅ Количество генераций <b>{int(message.text)}</b> успешно установлено',
                reply_markup=keyboard_close
            )
        else:
            await message.reply(f'⚠️ Минимальное кол-во генераций: {min_value_generation_value}, '
                                f'максимальное: {max_value_generation_value}')
    else:
        await message.reply('⚠️ Необходимо написать целое число')


@router.callback_query(lambda callback: callback.data == 'change_generate_number_params')
async def change_generate_number_params(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        '⚙️ <b>Введите диапозон чисел\nНапример: 1 100 (от 1 до 100)</b>',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_gen_command_number')
                ]
            ]
        )
    )
    await state.set_state(ChangeParams.allowable_values)


@router.message(ChangeParams.allowable_values)
async def change_params_generation_values(message: Message, state: FSMContext):
    await state.clear()
    split_message = message.text.split()

    if len(split_message) == 2:
        try:
            if int(split_message[0]) and int(split_message[1]):
                if int(split_message[0]) < int(split_message[1]):
                    last_data = await User(message.chat.id).get_last_generation_number()

                    last_data['min_value'] = int(split_message[0])
                    last_data['max_value'] = int(split_message[1])

                    await User(message.chat.id).update_generation_number_params(last_data)
                    await message.reply(
                        f'✅ Диапозон успешно установлен: '
                        f'от <b>{int(split_message[0])}</b> до <b>{int(split_message[1])}</b>',
                        reply_markup=keyboard_close
                    )
                else:
                    await message.reply('⚠️ Первое число должно быть меньше второго')
        except:
            await message.reply('⚠️ Необходимо написать целые числа')
    else:
        await message.reply('⚠️ Необходимо написать 2 числа (<b>от</b> и <b>до</b>)\n<b>Например:</b> 1 100')


# <--------------- / RANDOM PASSWORD / --------------->
@router.callback_query(lambda callback: callback.data == 'random_password')
async def random_password(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_password()

    await callback.message.edit_text(
        '🔑 <b>Случайный пароль</b>\n\n'
        f'🔁 Кол-во генераций: <b>{last_data["generation_count"]}</b>\n'
        f'📏 Длина пароля: <b>{last_data["password_size"]}</b>\n'
        f'🔣 Спец. символы: <b>{last_data["has_punctuation"]}</b>'
        .replace('True', 'вкл.').replace('False', 'выкл.'),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='-', callback_data='minus_generation_password_counter'),
                    InlineKeyboardButton(text=last_data["generation_count"],
                                         callback_data='change_generation_password_counter'),
                    InlineKeyboardButton(text='+', callback_data='plus_generation_password_counter')
                ],
                [
                    InlineKeyboardButton(text='🎲 Сгенерировать', callback_data='generate_password')
                ],
                [
                    InlineKeyboardButton(
                        text=f'Спец. символы: {last_data["has_punctuation"]}'
                        .replace('True', '✅')
                        .replace('False', '❌'),
                        callback_data='change_param_punctuation')
                ],
                [
                    InlineKeyboardButton(text='⚙️ Изменить длину пароля', callback_data='change_param_password_size')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_generation_commands')
                ]
            ]
        )
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.callback_query(lambda callback: callback.data == 'generate_password')
async def generate_password(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_password()

    punctuation = ''

    if last_data['has_punctuation']:
        punctuation = string.punctuation

    result = []
    for _ in range(last_data['generation_count']):
        result.append(
            ''.join([random.choice(string.ascii_letters + string.digits + punctuation)
                     for _ in range(last_data['password_size'])])
        )

    await callback.message.edit_text(
        '\n➖\n'.join(result),
        parse_mode=None,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='random_password')
                ]
            ]
        )
    )

    await asyncio.sleep(0.25)
    await AnswerCallbackQuery(callback_query_id=callback.id)


@router.callback_query(lambda callback: callback.data == 'change_param_punctuation')
async def change_param_punctuation(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_password()

    if last_data['has_punctuation'] is True:
        text = 'Вы выключили спец. символы'
        last_data['has_punctuation'] = False
    else:
        text = 'Вы включили спец. символы'
        last_data['has_punctuation'] = True

    await User(callback.message.chat.id).update_generation_password_params(last_data)

    await AnswerCallbackQuery(
        callback_query_id=callback.id,
        show_alert=True,
        text=text
    )

    await random_password(callback)


@router.callback_query(lambda callback: callback.data == 'minus_generation_password_counter')
async def minus_generation_password_counter(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_password()

    if last_data['generation_count'] > min_value_generation_value:
        last_data['generation_count'] -= 1
        await User(callback.message.chat.id).update_generation_password_params(last_data)
        await random_password(callback)
    else:
        await AnswerCallbackQuery(
            callback_query_id=callback.id,
            show_alert=True,
            text=f'⚠️ Минимальное допустимое количество генераций: {min_value_generation_value}'
        )


@router.callback_query(lambda callback: callback.data == 'plus_generation_password_counter')
async def plus_generation_password_counter(callback: CallbackQuery):
    last_data = await User(callback.message.chat.id).get_last_generation_password()

    if last_data['generation_count'] <= max_value_generation_value:
        last_data['generation_count'] += 1
        await User(callback.message.chat.id).update_generation_password_params(last_data)
        await random_password(callback)
    else:
        await AnswerCallbackQuery(
            callback_query_id=callback.id,
            show_alert=True,
            text=f'⚠️ Максимальное допустимое количество генераций: {max_value_generation_value}'
        )


@router.callback_query(lambda callback: callback.data == 'change_generation_password_counter')
async def change_generation_password_counter(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f'⚙️ <b>Введите количество генераций (от {min_value_generation_value} до {max_value_generation_value})</b>',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_gen_command_password')
                ]
            ]
        )
    )
    await state.set_state(ChangeParams.generation_count_password)


@router.message(ChangeParams.generation_count_password)
async def change_params_generation_password_count(message: Message, state: FSMContext):
    await state.clear()
    if message.text.isnumeric():
        if min_value_generation_value <= int(message.text) <= max_value_generation_value:
            last_data = await User(message.chat.id).get_last_generation_password()

            last_data['generation_count'] = int(message.text)

            await User(message.chat.id).update_generation_password_params(last_data)
            await message.reply(
                f'✅ Количество генераций <b>{int(message.text)}</b> успешно установлено',
                reply_markup=keyboard_close
            )
        else:
            await message.reply(f'⚠️ Минимальное кол-во генераций: {min_value_generation_value}, '
                                f'максимальное: {max_value_generation_value}')
    else:
        await message.reply('⚠️ Необходимо написать целое число')


@router.callback_query(lambda callback: callback.data == 'change_param_password_size')
async def change_param_password_size(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f'⚙️ <b>Введите длину пароля (от {min_password_size} до {max_password_size})</b>',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Вернуться', callback_data='back_to_gen_command_password')
                ]
            ]
        )
    )
    await state.set_state(ChangeParams.change_password_size)


@router.message(ChangeParams.change_password_size)
async def change_params_generation_password_size(message: Message, state: FSMContext):
    await state.clear()
    if message.text.isnumeric():
        if min_password_size <= int(message.text) <= max_password_size:
            last_data = await User(message.chat.id).get_last_generation_password()

            last_data['password_size'] = int(message.text)

            await User(message.chat.id).update_generation_password_params(last_data)
            await message.reply(
                f'✅ Длина пароля: <b>{int(message.text)}</b>',
                reply_markup=keyboard_close
            )
        else:
            await message.reply(f'⚠️ Минимальная длина пароля: <b>{min_password_size}</b>, максимальная: '
                                f'<b>{max_password_size}</b>')
    else:
        await message.reply('⚠️ Необходимо написать целое число')


# <--------------- / RANDOM NUMBER & PASSWORD / --------------->
@router.callback_query(lambda callback: callback.data.startswith('back_to_gen_command'))
async def back_to_gen_command(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    if callback.data.split('_')[-1] == 'number':
        await random_number(callback)
    else:
        await random_password(callback)


# <--------------- / RANDOM STRING / --------------->
@router.callback_query(lambda callback: callback.data == 'random_string')
async def random_string(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        '📃 <b>Отправьте .txt файл:</b>',
        reply_markup=keyboard_back_to_gen_commands
    )

    await state.set_state(GetData.get_file)


@router.message(GetData.get_file)
async def get_file_from_user(message: Message, state: FSMContext):
    await state.clear()
    try:
        if message.document.file_name[-3:] == 'txt':
            result = await get_random_string(message.document.file_id)
            await message.answer(f'📜 <b>Случайная запись:</b>\n{result}')
        else:
            await message.reply('<b>❌ Вам необходимо отправить файл с .txt расширением</b>')
    except AttributeError:
        await message.reply('<b>❌ Вам нужно прикрепить к сообщению файл с .txt расширением</b>')
