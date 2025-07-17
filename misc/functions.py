import os
import random
from aiohttp import ClientSession
from bots_starting import bot_tg, bot_vk


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/93.0.4577.82 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


async def generate_fact() -> str:
    url = 'https://randstuff.ru/fact/generate/'
    async with ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            data = await response.json(content_type='text/html')
            return data['fact']['text']


async def get_random_string(file_id):
    file_path = (await bot_tg.get_file(file_id)).file_path
    return_content = ''

    with open(f'files/{file_id}.txt', 'w', encoding='utf-8'):
        pass

    await bot_tg.download_file(file_path, f'files/{file_id}.txt')

    with open(f'files/{file_id}.txt', 'r', encoding='utf-8') as file:
        content = file.read().split()
        return_content = random.choice(content)

    os.remove(f'files/{file_id}.txt')
    return return_content


async def generate_winner(post_url: str) -> dict:
    try:
        post_data = post_url.split('-')[-1].split('_')
        owner_id, post_id = int(post_data[0]) * -1, int(post_data[-1])

        likes = (await bot_vk.api.likes.get_list(type="post", owner_id=owner_id, item_id=post_id)).items
        winner_id = random.choice(likes)

        user_info = (await bot_vk.api.users.get(user_id=winner_id, fields=['first_name', 'last_name']))[0]

        return {
            'username': f'{user_info.first_name} {user_info.last_name}',
            'user_url': f'https://vk.com/id{user_info.id}'
        }
    except:
        return {}
