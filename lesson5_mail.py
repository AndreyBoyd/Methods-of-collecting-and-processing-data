from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from pymongo import MongoClient
import time


chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
driver.get('https://mail.ru/')

# авторизуемся в почтовом ящике
login = driver.find_element_by_class_name('email-input')
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)

time.sleep(2)

passw = driver.find_element_by_class_name('password-input')
passw.send_keys('NextPassword172')
passw.send_keys(Keys.ENTER)

time.sleep(5)

# создаём список писем
letters_list = []

# создаём список с ссылками на страницы писем
mails_href = []
page_count = 0
end_of_page = False
mail_id_list = []
last_letter = None
while end_of_page == False:
    letters = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'js-tooltip-direction_letter-bottom')))
    if letters[-1] != last_letter:
        for letter in letters:
            mail_id = letter.get_attribute('data-uidl-id')
            if mail_id not in mail_id_list:
                mail_id_list.append(mail_id)
                mail_href = letter.get_attribute('href')
                mails_href.append(mail_href)
        page_count += 1
        last_letter = letters[-1]
    actions = ActionChains(driver)
    actions.key_down(Keys.ARROW_DOWN)
    actions.perform()
    try:
        driver.find_element_by_class_name('list-letter-spinner')
        end_of_page = True
    except:
        end_of_page = False

driver.implicitly_wait(10)

# открываем каждое письмо
for index, href in enumerate(mails_href):
    try:
        letter_data = {}
        driver.get(href)

        letter = driver.find_element_by_class_name('layout__letter-content')
        letter_head = letter.find_element_by_tag_name('h2').text
        letter_author = driver.find_element_by_class_name('letter__author')
        author_name = letter_author.find_element_by_class_name('letter-contact')
        author_email = author_name.get_attribute('title')
        author_name = author_name.text
        letter_date = letter_author.find_element_by_class_name('letter__date').text
        letter_body = driver.find_element_by_class_name('letter-body')
        l_body = letter_body.find_elements_by_tag_name('span')
        if len(l_body) == 0:
            l_body.append(letter_body.find_element_by_tag_name('div'))
        letter_text = ''
        for i in l_body:
            t = ''
            try:
                t = i.text
            except:
                print('Ошибка ')
            letter_text += t

        letter_data['head'] = letter_head
        letter_data['author_name'] = author_name
        letter_data['author_email'] = author_email
        letter_data['date'] = letter_date
        letter_data['text'] = letter_text
        letters_list.append(letter_data)

    except:
        print(f'Ошибка')

df = pd.DataFrame(letters_list)
df.to_csv('letters.csv', index=False)

# Записываем полученные данные в базу Mongo
client = MongoClient('localhost', 27017)
db = client['mailru_box']
db.mailru_box.delete_many({})
db.mailru_box.insert_many(letters_list)

driver.quit()
