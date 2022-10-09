import telethon
from telethon import TelegramClient, functions, types
from asyncio import run
import emoji
import re
import pandas as pd

API_ID = 12588462
API_HASH = '4a91f1fe83e1ebe18fc234b21d508d20'

channelName = 'mytar_rf'


async def channel_info(username, api_id, api_hash):
    async with TelegramClient('session', api_id, api_hash) as client:
        channel = await client.get_entity(username)
        messages = await client.get_messages(channel, limit=None)
        return messages


out = run(channel_info(channelName, API_ID, API_HASH))


def preprocessing_of_channel_telegrams(parser_output, name_chanel):
    titles, contents, dates = [], [], []
    for out_news in parser_output:

        bold_entiti = ''
        news_text = out_news.message
        news_entities = out_news.entities

        for entiti in news_entities:
            if type(entiti) == types.MessageEntityBold:
                bold_entiti = entiti
                break
        else:
            continue

        offset = bold_entiti.offset
        len = bold_entiti.length
        title = news_text[:offset + len + 1]
        news_text = news_text[offset + len - 1:]

        if name_chanel == 'mytar_rf':
            news_text.replace('@Mytar_rf', '')
        elif name_chanel == 'netipichniy_buh':
            news_text.replace('Курсы по 1С • Бух.юмор', '')

        news_text = ''.join(symbol for symbol in news_text if symbol not in emoji.EMOJI_DATA)
        title = ''.join(symbol for symbol in title if symbol not in emoji.EMOJI_DATA)
        myre = re.compile(
            u'(\u00a9|\u00ae|[\u2000-\u3300]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff])',
            re.UNICODE)
        news_text = re.sub(myre, '', news_text)
        title = re.sub(myre, '', title)

        title = " ".join(title.split())
        news_text = " ".join(news_text.split())


        titles.append(title)
        contents.append(news_text)
        dates.append(out_news.date)


    news_dataframe = pd.DataFrame({'title': titles, 'content': contents, 'date': dates})
    news_dataframe.content = news_dataframe['content'].apply(
        lambda x: x if len(x.split(' ')[0]) != 1 else x[2:])

    return news_dataframe
