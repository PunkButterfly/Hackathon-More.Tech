import requests as rq
from bs4 import BeautifulSoup as bs
import pandas as pd
import concurrent.futures
from datetime import datetime

URL = 'https://vc.ru/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/100.0.4896.88 Safari/537.36'}

HOST = 'https://vc.ru/'
FILE = 'vc.csv'


def get_html(url, params=None):
    return rq.get(url.strip(), headers=HEADERS, timeout=15, params=params)


def parse_page(page):
    html = get_html(URL + f'{page}')
    single_news_dict = {'title': None, 'content': None, 'date': None}
    parsed_page = None
    if html.status_code == 200:
        try:
            article = bs(html.text, 'html.parser').find('div', attrs={'class': 'page page--entry'})

            title = article.find('h1').get_text()

            article_paragraphs = article.find_all('p')
            article_paragraphs += article.find_all('li')
            content = ''
            for paragraph in article_paragraphs:
                content += str(paragraph.get_text())

            timestamp = article.find('time', attrs={'class': 'time'})['data-date']
            date = datetime.fromtimestamp(int(timestamp))

            single_news_dict['title'] = title
            single_news_dict['content'] = content
            single_news_dict['date'] = date

            parsed_page = pd.DataFrame([single_news_dict], columns=['title', 'content', 'date'])
        except AttributeError:
            print(f'Parsing {page} of pages faced to Error')
    return parsed_page


def parse(first_article, last_article):
    news = pd.DataFrame([], columns=['title', 'content', 'date'])
    html = get_html(URL)
    #
    pages = range(first_article, last_article)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        parsed_pages = executor.map(parse_page, pages)
    for parsed_page in parsed_pages:
        news = pd.concat([news, parsed_page], ignore_index=True)
    return news


parsed_news = parse(100001, 514973)  # 514973


path_to_drive = ""
parsed_news.to_csv(path_to_drive + FILE, index=False)
