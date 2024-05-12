from telethon import TelegramClient, events
from settings import api_id, api_hash
from db import InsertKeywordsToDb, DeleteKeywordsFromDb, InsertChannelToDb, DeleteChannelFromDb, GetKeywordsFromDb, \
    GetChannelsFromDb, InsertRSSToDb, DeleteRSSFromDb, SavePost, GetPosts, GetNewsText, Insert_chatid, DeletechatidFromDb\
    , GetKeywordsFromDbById, GetChannelsFromDbById, GetRSSFromDBById, Getchatids, InsertRelation
wordlen = 20
channellen = 100
rsslen = 100
def telegram_parser(session, api_id, api_hash, check_pattern_func=None,
                    send_message_func=None, logger=None, loop=None, bot=None):
    '''Телеграм парсер'''

    client = TelegramClient(session, api_id, api_hash,
                            base_logger=logger, loop=loop, system_version="4.16.30-vxCUSTOM")
    client.start()

    @bot.on(events.NewMessage(pattern='/start'))
    async def bot_settings(event):
        Insert_chatid(event.chat_id)
        await event.reply('Привет! Если хочешь добавить каналы, напиши /add_channel и вводи каналы в формате '
                          'channel_id:channel_link через пробел')
        await event.reply('Если хочешь удалить канал напиши /delete_channel и введи id каналов, которые хочешь '
                          'удалить через пробел')
        await event.reply('Если хочешь добавить ключевое слово для поиска, введи /add_keyword и слова через пробел')
        await event.reply('Если хочешь удалить ключевое слово, введи /delete_keyword и слова через пробел')
        await event.reply('Если хочешь добавить rss ресурк введи /add_rss, после чего введи в формате название_сайта,ссылка_на_rss_сайта')
        await event.reply('Для удаления rss введи /delete_rss и ссылку на rss')
        await event.reply('Для получения постов введи /get_posts и после него цифру - число постов. По умолчанию число постов равно 10.')

    @bot.on(events.NewMessage(pattern='/add_keyword'))
    async def add_words(event):
        key_words = GetKeywordsFromDbById(event.chat_id)
        censored = []
        try:
            keywords = list(map(str.lower, event.raw_text.split()[1::]))
            for i in keywords:
                if len(i) > wordlen:
                    censored.append(i)
                    await event.reply(f'Элемент {i} является слишком длинным и не будет добавлен')
                else:
                    if i in key_words:
                        censored.append(i)
                        await event.reply(f'Элемент {i} является повторным и не будет добавлен')
            for i in censored:
                keywords.remove(i)
            if keywords == []:
                await event.reply('Нет ключевых слов или все из них являются повторными либо слишком длинными')
            else:
                key_words += keywords
                InsertKeywordsToDb(keywords, event.chat_id)
                await event.reply('Ключевые слова добавлены')
        except Exception as e:
            await event.reply(f'Ошибка {e} при добавлении ключевых слов')

    @bot.on(events.NewMessage(pattern='/delete_keyword'))
    async def delete_words(event):
        key_words = GetKeywordsFromDbById(event.chat_id)
        keywords = list(map(str.lower, event.raw_text.split()[1::]))
        if keywords == []:
            await event.reply(f'Не введены ключевые слова')
        for i in keywords:
            try:
                DeleteKeywordsFromDb(i, event.chat_id)
                key_words.remove(i)
                await event.reply(f'Элемент {i} успешно удален')
            except Exception as e:
                if type(e) == ValueError:
                    await event.reply(f'Ошибка! Элемента {i} нет в таблице ключевых слов.')
                else:
                    await event.reply(f'Ошибка {e} при удалении элемента {i}.')

    @bot.on(events.NewMessage(pattern='/add_channel'))
    async def add_channels(event):
        inpchannels = event.raw_text.split()[1::]
        if inpchannels == []:
            await event.reply('Не введены каналы')
        for i in inpchannels:
            try:
                channeldata = i.split(',')
                if len(str(channeldata[1])) > channellen:
                    await event.reply(f'Название канала {i} является слишком длинным')
                else:
                    if int(channeldata[0]) in list(GetChannelsFromDbById(event.chat_id).keys()):
                        await event.reply(f'Канал {channeldata[0]} уже присутствует и не будет добавлен')
                    else:
                        InsertChannelToDb(channeldata, event.chat_id)
                        await event.reply(f'Канал {channeldata[0]} добавлен')
            except Exception as e:
                if type(e) == IndexError:
                    await event.reply(f'Неполный ввод, отсутствует id канала {channeldata[0]} или ссылка на канал')
                else:
                    await event.reply(f'Ошибка {e} при добавлении канала с id {channeldata[0]}')

    @bot.on(events.NewMessage(pattern='/delete_channel'))
    async def delete_channels(event):
        channelids = event.raw_text.split()[1::]
        if channelids == []:
            await event.reply('Не введены каналы')
        for i in channelids:
            try:
                if int(i) not in list(GetChannelsFromDbById(event.chat_id).keys()):
                    await event.reply(f'Канала {i} нет в таблице')
                else:
                    DeleteChannelFromDb(i, event.chat_id)
                    await event.reply(f'Элемент {i} успешно удален')
            except Exception as e:
                if type(e) == ValueError:
                    await event.reply(f'Ошибка, {i} не является id канала')
                else:
                    await event.reply(f'Ошибка {e} при удалении элемента {i}. Скорее всего его нет в списке каналов')

    @bot.on(events.NewMessage(pattern='/add_rss'))
    async def add_rss(event):
        rss = event.raw_text.split()[1::]
        if rss == []:
            await event.reply('Нет RSS')
        for i in rss:
            try:
                rssdata = i.split(',')
                if len(str(rssdata[1])) > channellen or len(str(rssdata[0])) > rsslen:
                    await event.reply(f'Название rss {i} является слишком длинным или rss ссылка является слишком длинной')
                else:
                    if rssdata[1] in list(GetRSSFromDBById(event.chat_id).keys()):
                        await event.reply(f'rss {rssdata[0]} уже присутствует в таблице и не будет добавлен')
                    else:
                        InsertRSSToDb(rssdata, event.chat_id)
                        await event.reply(f'rss {rssdata[0]} добавлен')
            except Exception as e:
                if type(e) == IndexError:
                    await event.reply(f'Неполный ввод, отсутствует название rss {rssdata[0]} или ссылка на rss')
                else:
                    await event.reply(f'Ошибка {e} при добавлении rss с названием {rssdata[0]}')

    @bot.on(events.NewMessage(pattern='/delete_rss'))
    async def delete_rss(event):
        rsslinks = event.raw_text.split()[1::]
        if rsslinks == []:
            await event.reply('Нет ссылок для удаления')
        for i in rsslinks:
            try:
                if i not in list(GetRSSFromDBById(event.chat_id).keys()):
                    await event.reply(f'Rss {i} нет в таблице, поэтому он не будет удален')
                else:
                    DeleteRSSFromDb(i)
                    await event.reply(f'Элемент {i} успешно удален')
            except Exception as e:
                await event.reply(f'Ошибка {e} при удалении элемента {i}. Скорее всего его нет в списке rss')

    @bot.on(events.NewMessage(pattern='/get_posts'))
    async def print_posts(event):
        text = event.raw_text.split()[1::]
        try:
            if text[0].isnumeric() and int(text[0]) > 0:
                count = int(text[0])
            else:
                count = 10
        except Exception as e:
            count = 10
        posts = GetPosts(count, event.chat_id)
        if posts == []:
            await event.reply('Новостей пока что больше нет!')
        for post in posts:
            try:
                full_post = f'<b>{post[1]}</b>\n{post[2]}\n{post[0]}'
                await send_message_func(full_post)
            except Exception as e:
                await event.reply(f'Ошибка {e}')

    @bot.on(events.NewMessage(pattern='/exit'))
    async def delete_user(event):
        DeletechatidFromDb(event.chat_id)

    @client.on(events.NewMessage(chats=list(GetChannelsFromDb().values())))
    async def handler(event):
        '''Забирает посты из телеграмм каналов и посылает их в наш канал'''
        if event.raw_text == '':
            return
        news_text = ' '.join(event.raw_text.split('\n')[:2])

        if not (check_pattern_func is None):
            if not check_pattern_func(news_text, GetKeywordsFromDb()):
                return
        if news_text in GetNewsText():
            return
        source = GetChannelsFromDb()[int(event.message.peer_id.channel_id)]

        link = f'{source}/{event.message.id}'

        channel = '@' + source.split('/')[-1]

        id = SavePost(news_text, channel, link)

        for i in Getchatids():
            if check_pattern_func(news_text, GetKeywordsFromDbById(i)):
                if source in GetChannelsFromDbById(i).values():
                    InsertRelation(i, id)

    return client

