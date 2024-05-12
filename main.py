import httpx
import asyncio
import logging
from collections import deque
from telethon import TelegramClient, events
from telegram_parser import telegram_parser
from utils import create_logger, send_error_message
from settings import api_id, api_hash, gazp_chat_id, bot_token
from rss_parser import rss_parser
from db import GetRSSFromDB, DeletePost
import random

cur_rss_channels = GetRSSFromDB()

def check_pattern_func(text, key_words):
    '''Вибирай только посты или статьи про газпром или газ'''
    words = text.lower().split()
    for word in words:
        for key in key_words:
            if key in word:
                return True

    return False

# +/- интервал между запросами у rss в секундах
timeout = 120

logger = create_logger('gazp')
logger.info('Start...')

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tele_logger = create_logger('telethon', level=logging.ERROR)

bot = TelegramClient('bot', api_id, api_hash,
                     base_logger=tele_logger, loop=loop, system_version="4.16.30-vxCUSTOM")
bot.start(bot_token=bot_token)


async def send_message_func(text):
    '''Отправляет посты в канал через бот'''
    await bot.send_message(entity=gazp_chat_id,
                           parse_mode='html', link_preview=False, message=text)

    logger.info(text)

# Телеграм парсер
client = telegram_parser('gazp', api_id, api_hash, check_pattern_func, send_message_func, tele_logger, loop, bot)

httpx_client = httpx.AsyncClient()

loop.create_task(DeletePost())


for rss_link, source in cur_rss_channels.items():

    async def wrapper(source, rss_link):

        try:
            await rss_parser(httpx_client, source, rss_link, timeout, check_pattern_func, send_message_func, logger)
        except Exception as e:
            message = f'ERROR: {source} parser is down! \n{e}'
            await send_error_message(message, bot_token, gazp_chat_id, logger)

    loop.create_task(wrapper(source, rss_link))

async def update_rss(cur_rss_channels, timeout):
    while True:
        new_rss_channels = GetRSSFromDB()
        for rss_link, source in new_rss_channels.items():
            if rss_link not in cur_rss_channels.keys():
                loop.create_task(wrapper(source, rss_link))
                print(f'task {source} created')
        cur_rss_channels = new_rss_channels
        await asyncio.sleep(timeout * 2 - random.uniform(0, 0.5))
loop.create_task(update_rss(cur_rss_channels, timeout))

try:
    client.run_until_disconnected()

except Exception as e:
    message = f'ERROR: telegram parser (all parsers) is down! \n{e}'
    loop.run_until_complete(send_error_message(message, bot_token,
                                               gazp_chat_id, logger))
finally:
    loop.run_until_complete(httpx_client.aclose())
    loop.close()
