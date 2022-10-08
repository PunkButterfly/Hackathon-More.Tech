import requests
from bs4 import BeautifulSoup as BS
import pandas as pd


def get_pages(weeks_in_year, begin_year, end_period, pattern):
    output_pages = []
    for i in range(3):
        for j in range(weeks_in_year):
            if i + begin_year == end_period[1] and j == end_period[0]:
                break
            output_pages.append(pattern + str(j) + '-' + str(begin_year + i))
        if i + begin_year == end_period[1]:
            break
    return output_pages


def get_articles(links):
    article_links = []
    for url in links:
        response = requests.get(url)
        soup = BS(response.text, 'lxml')
        for a in soup.find_all('a', {"class": "news_block_hdg"}):
            article_links.append('https://glavkniga.ru' + a['href'])
    return article_links


def get_content(article_links):
    data = []
    for url in article_links:
        response = requests.get(url)
        soup = BS(response.text, 'lxml')
        title = soup.find_all('h1')[0].text
        content = ' '.join(soup.find_all('div', id="news_body")[0].text.split())
        date = soup.find_all('div', id='news_flags_date')[0].text
        data.append([title, content, date])
    return data


weeks_in_year = 52
pattern = "https://glavkniga.ru/news/?week="
week_number = "2"
begin_year = 2020
end_period = (41, 2022)

pages = get_pages(weeks_in_year, begin_year, end_period, pattern)
articles = get_articles(pages)
parsed_content = get_content(articles)

dataF = pd.DataFrame(parsed_content, columns=['title', 'content', 'date'])
dataF.to_csv('glavkniga.csv')
