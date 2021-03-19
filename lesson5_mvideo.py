from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from pymongo import MongoClient
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint
from selenium.webdriver.common.action_chains import ActionChains
import ast

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')
time.sleep(5)

button = driver.find_element_by_css_selector('a.c-btn_icon')

# не мудрствуя лукаво жмём кнопку прокрутки 7 раз c запасом :)
for i in range(7):
    button.click()
    time.sleep(3)

products = driver.find_elements_by_xpath('.//ul[contains(@data-init-param,"Хиты продаж")]//li')

products_list = []

for product in products:
    product_info = {}

    product_name = product.find_element_by_tag_name('h4').get_attribute('title')
    product_link = product.find_element_by_tag_name('a').get_attribute('href')
    info = product.find_element_by_tag_name('a').get_attribute('data-product-info')

    info = ast.literal_eval(info)

    product_info['name'] = product_name
    product_info['product_category'] = info['productCategoryName']
    product_info['product_link'] = product_link
    product_info['product_price'] = info['productPriceLocal']
    product_info['product_manufacturer'] = info['productVendorName']

    products_list.append(product_info)

pprint(products_list)

# Записываем полученные данные в базу Mongo
client = MongoClient('localhost', 27017)
db = client['mvideo']
db.mvideo.delete_many({})
db.mvideo.insert_many(products_list)

driver.quit()

