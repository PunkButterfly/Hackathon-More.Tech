import requests as rq
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
from tqdm import tqdm

URL = 'https://svoedeloplus.ru/category/novosti'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/100.0.4896.88 Safari/537.36'}

HOST = 'https://svoedeloplus.ru'
FILE = 'svoedelo.csv'


def get_html(url, params=None):
    return rq.get(url.strip(), headers=HEADERS, timeout=15, params=params)


def get_content(html):
    soup = bs(html.text, 'html.parser')
    items = soup.find('div', attrs={'class': 'post-boxes'}).find_all('div')

    news_page = pd.DataFrame([], columns=['title', 'content', 'date'])
    for item in items:
        try:
            single_news_dict = {'title': None, 'content': None, 'date': None}
            link_to_single_news = item.find('a').get('href')

            single_news = get_html(link_to_single_news).text
            article = bs(single_news, 'html.parser').find('article')

            title = article.find('h1').get_text()

            article_paragraphs = article.find_all('p')
            article_paragraphs += article.find_all('li')
            content = ''
            for paragraph in article_paragraphs:
                content += str(paragraph.get_text())

            date = article.find('time')['datetime']

            single_news_dict['title'] = title
            single_news_dict['content'] = content
            single_news_dict['date'] = date

            news_page = pd.concat([news_page, pd.DataFrame([single_news_dict], columns=['title', 'content', 'date'])],
                                  ignore_index=True)
        except Exception:
            # print('Did not work!')
            continue
    return news_page


def parse(number_of_pages):
    news = pd.DataFrame([], columns=['title', 'content', 'date'])
    html = get_html(URL)
    failed_pages = []
    if html.status_code == 200:
        for page in tqdm(range(1, number_of_pages)):
            print(URL + f'/page/{page}/')
            html = get_html(URL + f'/page/{page}/')
            try:
                news_page = get_content(html)
                print(news_page)
                news = pd.concat([news, news_page], ignore_index=True)
            except AttributeError:
                print(f'Parsing {page} of pages faced to Error')
                try:
                    news_page = get_content(html)
                    news = pd.concat([news, news_page], ignore_index=True)
                except Exception:
                    failed_pages.append(page)
                    print('Parser failed to bypass the exception')
                    continue
        print('Parsing is completed!')
    else:
        print('Did not get connection to svoedeloplus.ru!/n Parsing faced to error')
    return news, failed_pages


parsed_news = parse(6)

print(f'Failed pages: {parsed_news[1]}')

path_to_drive = ""
parsed_news[0].to_csv(path_to_drive + FILE, index=False)
