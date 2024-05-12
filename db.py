import sqlite3
import datetime
import asyncio
# Устанавливаем соединение с базой данных
connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

cursor.execute("PRAGMA foreign_keys = ON")
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_ids (
id INTEGER PRIMARY KEY,
chatid INTEGER NOT NULL UNIQUE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS keywords (
id INTEGER PRIMARY KEY,
keyword TEXT NOT NULL,
chatid INTEGER NOT NULL,
FOREIGN KEY (chatid) REFERENCES chat_ids (chatid) ON DELETE CASCADE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS channels (
id INTEGER PRIMARY KEY,
channelid INTEGER NOT NULL,
channellink TEXT NOT NULL,
chatid INTEGER NOT NULL,
FOREIGN KEY (chatid)  REFERENCES chat_ids (chatid) ON DELETE CASCADE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS rss (
id INTEGER PRIMARY KEY,
sitename TEXT,
sitelink TEXT NOT NULL,
chatid INTEGER NOT NULL,
FOREIGN KEY (chatid) REFERENCES chat_ids (chatid) ON DELETE CASCADE
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS post (
id INTEGER PRIMARY KEY,
news_text TEXT,
source TEXT,
source_link TEXT,
time INTEGER,
flag INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS status (
id INTEGER PRIMARY KEY,
chatid INTEGER NOT NULL,
postid INTEGER NOT NULL,
flag INTEGER,
FOREIGN KEY (chatid)  REFERENCES chat_ids (chatid) ON DELETE CASCADE,
FOREIGN KEY (postid)  REFERENCES post (id) ON DELETE CASCADE
)
''')

timeout = 120

def InsertKeywordsToDb(keywords, chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    for i in keywords:
        cursor.execute('INSERT INTO keywords (keyword, chatid) VALUES (?,?)', (i, chatid,))
    connection.commit()
    connection.close()

def DeleteKeywordsFromDb(keyword, chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('DELETE FROM keywords WHERE keyword = ? AND chatid = ?', (keyword, chatid,))
    connection.commit()
    connection.close()

def GetKeywordsFromDb():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    keywords = []
    cursor.execute('SELECT keyword FROM keywords')
    keywordsdb = list(map(list, cursor.fetchall()))
    for i in keywordsdb:
        i = str(i[0])
        if i not in keywords:
            keywords.append(i)
    connection.close()
    return keywords

def GetKeywordsFromDbById(chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    keywords = []
    cursor.execute('SELECT keyword FROM keywords WHERE chatid = ?', (chatid,))
    keywordsdb = list(map(list, cursor.fetchall()))
    for i in keywordsdb:
        i = str(i[0])
        if i not in keywords:
            keywords.append(i)
    connection.close()
    return keywords

def InsertChannelToDb(channel, chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('INSERT INTO channels (channelid, channellink, chatid) VALUES (?,?,?)', (channel[0], channel[1], chatid,))
    connection.commit()
    connection.close()

def DeleteChannelFromDb(channel, chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('DELETE FROM channels WHERE channelid = ? AND chatid = ?', (channel, chatid))
    connection.commit()
    connection.close()

def GetChannelsFromDb():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    telegram_channels = {}
    cursor.execute('SELECT * FROM channels')
    channels = list(map(list, cursor.fetchall()))
    for i in channels:
        telegram_channels[i[1]] = i[2]
    connection.close()
    return telegram_channels

def GetChannelsFromDbById(chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    telegram_channels = {}
    cursor.execute('SELECT * FROM channels WHERE chatid=?', (chatid,))
    channels = list(map(list, cursor.fetchall()))
    for i in channels:
        telegram_channels[i[1]] = i[2]
    connection.close()
    return telegram_channels

def InsertRSSToDb(link, chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('INSERT INTO rss (sitename, sitelink, chatid) VALUES (?, ?, ?)', (link[0], link[1], chatid))
    connection.commit()
    connection.close()

def DeleteRSSFromDb(link):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('DELETE FROM rss WHERE sitelink = ?', (link, ))
    connection.commit()
    connection.close()

def GetRSSFromDB():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    RSS = {}
    cursor.execute('SELECT * FROM rss')
    rssdata = list(map(list, cursor.fetchall()))
    for i in rssdata:
        RSS[i[2]] = i[1]
    connection.close()
    return RSS

def GetRSSFromDBById(chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    RSS = {}
    cursor.execute('SELECT * FROM rss where chatid = ?', (chatid, ))
    rssdata = list(map(list, cursor.fetchall()))
    for i in rssdata:
        RSS[i[2]] = i[1]
    connection.close()
    return RSS

def SavePost(news_text, source, source_link):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('INSERT INTO post (news_text, source, source_link, time, flag) VALUES (?, ?, ?, ?, 0)', (news_text, source, source_link, datetime.datetime.now().timestamp(), ))
    connection.commit()
    connection.close()
    return cursor.lastrowid

async def DeletePost():
    while True:
        connection = sqlite3.connect('my_database.db')
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute('DELETE FROM post WHERE time+7200 < (?) ', (datetime.datetime.now().timestamp(), ))
        connection.commit()
        connection.close()
        await asyncio.sleep(timeout)

def GetPosts(count, chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('SELECT * FROM status JOIN post on status.postid = post.id WHERE status.flag=0 AND status.chatid = (?) ORDER BY id LIMIT (?)', (chatid, count,))
    posts = list(map(list, cursor.fetchall()))
    result = [i[5:8] for i in posts]
    cursor.execute('WITH q AS (SELECT id FROM status WHERE status.flag=0 AND status.chatid = (?) ORDER BY id LIMIT (?)) UPDATE status SET flag = 1  WHERE id in q', (chatid, count,))
    #cursor.execute('SELECT news_text, source, source_link FROM post WHERE flag = 0 ORDER BY id LIMIT (?)', (count, ))
    #posts = list(map(list, cursor.fetchall()))
    #cursor.execute('WITH q AS (SELECT id FROM post WHERE flag = 0 ORDER BY id LIMIT (?)) UPDATE post SET flag = 1  WHERE id in q', (count, ))
    connection.commit()
    connection.close()
    return result

def GetNewsText():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('SELECT news_text FROM post')
    posttexts = list(map(list, cursor.fetchall()))
    for i in range(len(posttexts)):
        posttexts[i] = str(posttexts[i]).strip('[]\'').split('\\n')[0].replace('\\xa0', ' ')
    connection.commit()
    connection.close()
    return posttexts

def Insert_chatid(chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        cursor.execute('INSERT INTO chat_ids (chatid) VALUES (?)', (chatid,))
        print('добавлено')
    except Exception as e:
        print(e)
    connection.commit()
    connection.close()

def DeletechatidFromDb(chatid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('DELETE FROM chat_ids WHERE chatid = ?', (chatid, ))
    connection.commit()
    connection.close()

def Getchatids():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    chatids = []
    cursor.execute('SELECT chatid FROM chat_ids')
    chatidsdb = list(map(list, cursor.fetchall()))
    for i in chatidsdb:
        if i not in chatids:
            chatids.append(i[0])
    connection.close()
    return chatids

def InsertRelation(chatid, postid):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    try:
        cursor.execute('INSERT INTO status (chatid, postid, flag) VALUES (?, ?, ?)', (chatid, postid, 0))
    except Exception as e:
        print(e)
    connection.commit()
    connection.close()

connection.commit()
connection.close()