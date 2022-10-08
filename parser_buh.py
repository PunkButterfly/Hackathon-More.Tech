import requests as rq
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import concurrent.futures

URL = 'https://buh.ru/news'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/100.0.4896.88 Safari/537.36'}

HOST = 'https://buh.ru'
FILE = 'buh.csv'


def get_html(url, params=None):
    return rq.get(url.strip(), headers=HEADERS, timeout=15, params=params)


def get_content(html):
    soup = bs(html.text, 'html.parser')
    items = soup.find_all('article', attrs={'class': 'article'})

    news_page = pd.DataFrame([], columns=['title', 'content', 'date'])
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            parsed_items = executor.map(parse_item, items)
        for parsed_item in parsed_items:
            news_page = pd.concat([news_page, parsed_item], ignore_index=True)
    except Exception:
        print('Did not work!')
        # time.sleep(2)
    return news_page


def parse_item(item):
    single_news_dict = {'title': None, 'content': None, 'date': None}
    link_to_single_news = HOST + item.find('a').get('href')

    single_news = get_html(link_to_single_news).text
    article = bs(single_news, 'html.parser').find('section', attrs={'class': 'content_page'})

    title = article.find('h1').get_text()

    article_paragraphs = article.find_all('p')
    content = ''
    for paragraph in article_paragraphs:
        content += str(paragraph.get_text())

    date = article.find('span', attrs={'class': 'grayd'}).get_text()

    single_news_dict['title'] = title
    single_news_dict['content'] = content
    single_news_dict['date'] = date
    parsed_item = pd.DataFrame([single_news_dict], columns=['title', 'content', 'date'])
    return parsed_item


def parse_page(url):
    html = get_html(url)
    news_page = None
    try:
        news_page = get_content(html)
    except AttributeError:
        print(f'Parsing faced to Error')
        try:
            time.sleep(2)
            news_page = get_content(html)
        except Exception:
            print('Parser failed to bypass the exception')
    return news_page


def parse(number_of_pages):
    news = pd.DataFrame([], columns=['title', 'content', 'date'])
    html = get_html(URL)
    if html.status_code == 200:
        pages = [URL + f'/?PAGEN_1={x}' for x in range(1, number_of_pages)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            parsed_pages = executor.map(parse_page, pages)
        for parsed_page in parsed_pages:
            news = pd.concat([news, parsed_page], ignore_index=True)
        print('Parsing is completed!')
    else:
        print('Did not get connection to secretmag.ru!/n Parsing faced to error')
    return news


parsed_news = parse(1001)

path_to_drive = ""
parsed_news.to_csv(path_to_drive + FILE, index=False)
# супер-рабочая
