import random
import asyncio
from collections import deque
import httpx
import feedparser
from db import GetKeywordsFromDb, SavePost, GetNewsText
from utils import random_user_agent_headers
from db import GetRSSFromDB, Getchatids, GetKeywordsFromDbById, GetRSSFromDBById, InsertRelation


async def rss_parser(httpx_client, source, rss_link, timeout=120, check_pattern_func=None, send_message_func=None, logger=None):
    '''Парсер rss ленты'''
    while True:
        if rss_link not in GetRSSFromDB().keys():
            break
        try:
            response = await httpx_client.get(rss_link, headers=random_user_agent_headers())
            response.raise_for_status()
        except Exception as e:
            if not (logger is None):
                logger.error(f'{source} rss error pass\n{e}')

            await asyncio.sleep(timeout * 2 - random.uniform(0, 0.5))
            continue

        feed = feedparser.parse(response.text)

        for entry in feed.entries[:20][::-1]:
            if 'summary' not in entry and 'title' not in entry:
                continue

            summary = entry['summary'] if 'summary' in entry else ''
            title = entry['title'] if 'title' in entry else ''

            news_text = f'{title}\n{summary}'
            if not (check_pattern_func is None):
                if not check_pattern_func(news_text, key_words=GetKeywordsFromDb()):
                    continue

            if title.replace('\xa0', ' ') in GetNewsText():
                continue
            link = entry['link'] if 'link' in entry else ''

            id = SavePost(news_text, source, link)

            for i in Getchatids():
                if check_pattern_func(news_text, GetKeywordsFromDbById(i)):
                    if source in GetRSSFromDBById(i).values():
                        InsertRelation(i, id)

        await asyncio.sleep(timeout - random.uniform(0, 0.5))
    if logger == None:
        print(f'Парсер {source} успешно завершил работу')
    else:
        logger.info(f'Парсер {source} успешно завершил работу')