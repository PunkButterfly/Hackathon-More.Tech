import requests as rq
from bs4 import BeautifulSoup as bs
import time
import csv
import pandas as pd
from tqdm import tqdm

URL = 'https://secretmag.ru/investment'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                         ' AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/100.0.4896.88 Safari/537.36'}

HOST = 'https://secretmag.ru'
FILE = 'news_secretmag.csv'


def get_html(url, params=None):
    return rq.get(url.strip(), headers=HEADERS, timeout=15, params=params)


# def get_count_of_pages(html):
#     soup = bs(html, 'html.parser')
#     pagination = soup.find('span', class_='pagination-data').get_text()
#     # pagination = pagination[pagination.find('of') + 3:len(pagination) - 1]
#     return print(pagination)  # int(pagination) // 50


def get_content(html):
    soup = bs(html.text, 'html.parser')
    items = soup.find_all(attrs={'data-qa': 'lb-block'})

    news_page = pd.DataFrame([], columns=['title', 'content', 'date'])
    for item in items:
        try:
            time.sleep(2)
            single_news_dict = {'title': None, 'content': None, 'date': None}
            link_to_single_news = HOST + item.find('a').get('href')

            single_news = get_html(link_to_single_news).text
            article = bs(single_news, 'html.parser').find('article')

            title = article.find('h1').get_text()

            article_paragraphs = article.find_all('p')
            content = ''
            for paragraph in article_paragraphs:
                content += str(paragraph.get_text())
            #_1Lg_CbTX _240YeLMx

            date = article.find(attrs={'class': '_1Lg_CbTX _240YeLMx'}).get_text()

            single_news_dict['title'] = title
            single_news_dict['content'] = content
            single_news_dict['date'] = date

            news_page = pd.concat([news_page, pd.DataFrame([single_news_dict], columns=['title', 'content', 'date'])],
                             ignore_index=True)
            # print(news_page)
        except Exception:
            print('Did not work!')
            time.sleep(2)
            continue
    return news_page


def parse(number_of_pages):
    news = pd.DataFrame([], columns=['title', 'content', 'date'])
    html = get_html(URL)
    failed_pages = []
    if html.status_code == 200:
        for page in tqdm(range(0, number_of_pages)):
            html = get_html(URL, params={'page': page})
            try:
                print(f'Вызвана get_content')
                news_page = get_content(html)
                print('get_content отработала')
                print(news.shape)
                print(news_page)

                print(news_page.shape)
                print(news_page)
                news = pd.concat([news, news_page], ignore_index=True)
            except AttributeError:
                print(f'Parsing {page} of pages faced to Error')
                try:
                    time.sleep(10)
                    news_page = get_content(html)
                    print(news_page)
                    news = pd.concat([news, pd.DataFrame([news_page], columns=['title', 'content', 'date'])],
                                     ignore_index=True)
                except Exception:
                    failed_pages.append(page)
                    print('Parser failed to bypass the exception')
                    continue
        print('Parsing is completed!')
    else:
        print('Did not get connection to secretmag.ru!/n Parsing faced to error')
    return news


parsed_news = parse(1)

path_to_drive = ""
parsed_news.to_csv(path_to_drive + "secretmag.csv", index=False)
