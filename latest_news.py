from datetime import datetime
from pprint import pprint

import requests
from lxml import html
from pymongo import MongoClient

# ================================================= Config Data Base

client = MongoClient('127.0.0.1', 27017)

db = client['russian_news']

db_ya_news = db.yandex_news


# ================================================= End

# ================================================= Methods

def format_string(str_element):
    """Get rid of unwanted symbols"""
    return str_element.replace(u'\xa0', u' ')


# ================================================= End

# ================================================= Collecting Data

# Address to use
url = 'https://yandex.ru/news/'

# Set User-Agent
header = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:93.0) Gecko/20100101 Firefox/93.0'}

# Get page source as a result of request
response = requests.get(url)

# Convert page source code, into a string
dom = html.fromstring(response.text)

news_titles = dom.xpath('//h2[@class="mg-card__title"]/text()')
news_link = dom.xpath('//h2[@class="mg-card__title"]/../@href')
news_source = dom.xpath('//a[@class="mg-card__source-link"]/text()')
news_published_at = dom.xpath('//span[@class="mg-card-source__time"]/text()')

# ================================================= End

# ================================================= Data Processing

tmp_length = len(news_titles)
news_list = []
if all(len(lst) == tmp_length for lst in [news_link, news_source, news_published_at]):

    # Create Dict 
    news = {}

    for i in range(tmp_length):
        news['source'] = news_source[i]
        news['title'] = format_string(news_titles[i])
        news['link'] = news_link[i]
        news['date'] = f'{datetime.date(datetime.now())} {news_published_at[i]}'
        news_copy = news.copy()
        news_list.append(news_copy)


else:
    print('\'titles\', \'links\', \'sources\' and \'times\' are not the same qty !')

# ================================================= End

# ================================================= Append to DB
db_ya_news.insert_many(news_list)

for doc in db_ya_news.find({}):
    pprint(doc)

# ================================================= End
