import logging
import aiogram
import vkbottle
from os import getenv
from dotenv import load_dotenv


load_dotenv()
logging.disable(20)


bot_tg = aiogram.Bot(token=getenv('TOKEN_TELEGRAM'), parse_mode='HTML')
bot_vk = vkbottle.Bot(getenv('TOKEN_VK'))
