# Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.

import requests
from lxml import html
from pprint import pprint
from datetime import datetime

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}
news = []

# lenta.ru
main_url = 'https://lenta.ru'
response = requests.get(main_url, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath('//div[@class="span4"]/div[@class="item"]')

for item in items:
    news_item = {}
    name = item.xpath('.//a/text()')[0].replace('\xa0', ' ')
    link = item.xpath('.//a/@href')[0]
    lenta_date = item.xpath('.//time/@datetime')

    news_item['name'] = name
    news_item['link'] = main_url + link
    news_item['date'] = lenta_date
    news.append(news_item)
    news_item['source'] = 'lenta.ru'

# yandex-новости
main_url = 'https://yandex.ru/'
response = requests.get(main_url, headers=header)

dom = html.fromstring(response.text)
items = dom.xpath('//ol/li')
yandex_date = datetime.today().strftime("%d-%m-%Y")

for item in items:
    news_item = {}
    source = item.xpath('.//object/@title')[0]
    name = item.xpath('.//span[contains(@class ,"news__item-content")]/text()')[0].replace('\xa0', ' ')
    link = item.xpath('.//a/@href')[0]

    news_item['source'] = source
    news_item['link'] = link
    news_item['name'] = name
    news_item['date'] = yandex_date

    news.append(news_item)

# news.mail.ru
def get_the_source_baby(link):

    response = requests.get(link, headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath('//div[contains(@class,"article js-article")]')

    for item in items:
        source = item.xpath('.//span[@ class ="link__text"]/text()')[0]

    return source

main_url = 'https://news.mail.ru'
response = requests.get(main_url, headers=header)
dom = html.fromstring(response.text)
items = dom.xpath('//a[contains(@class,"photo photo_full photo_scale")] | //a[contains(@class,"photo photo_small photo_scale photo_full js-topnews__item")] ')
mail_ru_date = datetime.today().strftime("%d-%m-%Y")  # идём по пути наименьшего сопротивления :)

i = 0  # перебераем внешние ссылки для добавления источника
for item in items:
    news_item = {}
    name = item.xpath('.//span[@class="photo__title photo__title_new photo__title_new_hidden js-topnews__notification"]/text()')[0].replace('\xa0', ' ')
    link = item.xpath('//a[contains(@class, "js-topnews__item")]/@href')[i]

    news_item['name'] = name
    news_item['link'] = link

    source = get_the_source_baby(link)
    news_item['source'] = source
    news_item['date'] = mail_ru_date

    news.append(news_item)
    i += 1

pprint(news)