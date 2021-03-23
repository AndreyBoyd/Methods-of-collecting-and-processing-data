# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import re

class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books

    def process_item(self, item, spider):
        if item['book_name']:
            item['book_name'] = str(re.sub('\n', '', item['book_name']))
        if item['book_old_price']:
            item['book_old_price'] = int(re.sub('\D', '', item['book_old_price'][0].split(' ')[0]))
        else:
            item['book_old_price'] = None
        if item['book_new_price']:
            item['book_new_price'] = int(re.sub('\D', '', item['book_new_price'][0]))
        else:
            item['book_price_sale'] = None
        if item['book_rating']:
            item['book_rating'] = item['book_rating'][0]
        else:
            item['book_rating'] = None

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
