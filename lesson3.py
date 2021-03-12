# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

# собираем данные и помещаем их в json файл
import use as use
from bs4 import BeautifulSoup as bs
import requests
import json
import pandas as pd
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['vacancies']
jobs = db.jobs

def _parser_superjob(vacancy):
    vacancy_data = []
    main_link = 'https://russia.superjob.ru'
    link = 'https://www.superjob.ru/vacancy/search/'
    params = {'keywords': vacancy,
              'profession_only': '1',
              'geo[c][0]': '15',
              'geo[c][1]': '1',
              'geo[c][2]': '9',
              'page': '',
              'noGeo': '1'
              }
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

    response = requests.get(main_link + '/vacancy/search/', params=params, headers=headers)
    if response.ok:
       soup = bs(response.text, 'html.parser')
       page_block = soup.find('a', {'class': 'f-test-button-1'})
    if not page_block:
        last_page = 1
    else:
        page_block = page_block.findParent()
        last_page = int(page_block.find_all('a')[-2].getText())

    for page in range(0, last_page + 1):
        params['page'] = page
        response = requests.get(link, params=params, headers=headers)

        if response.ok:
            parsed_response = bs(response.text, 'html.parser')
            vacancy_items = parsed_response.find_all('div', {'class': 'f-test-vacancy-item'})

            for item in vacancy_items:
                vacancy_data.append(_parser_item_superjob(item))

    return vacancy_data

def _parser_item_superjob(item):

        vacancy_data = {}

        # vacancy_name
        vacancy_name = item.find_all('a')
        vacancy_data['vacancy_name'] = vacancy_name[0].getText()

        # salary
        salary = item.find('span', {'class': 'f-test-text-company-item-salary'}).findChild().text
        if salary == 'По договорённости':
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.replace(u'\xa0', ' ').split()
            salary_currency = salary.pop()
            if salary[0] == 'от':
                salary.remove('от')
                salary_min = float(''.join(salary[i] for i in range(len(salary))))
                salary_max = None
            elif salary[0] == 'до':
                salary.remove('до')
                salary_min = None
                salary_max = float(''.join(salary[i] for i in range(len(salary))))
            else:
                salary = ''.join(salary[i] for i in range(len(salary))).split('—')
                salary_min = float(salary[0])
                salary_max = float(salary[1]) if len(salary) > 1 else float(
                    salary[0])
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency

        # link
        vacancy_link = item.find_all('a')
        vacancy_link = vacancy_link[0]['href']
        vacancy_data['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'

        # site
        vacancy_data['site'] = 'www.superjob.ru'

        return vacancy_data


def parser_vacancy(vacancy):
    vacancy_data = []
    vacancy_data.extend(_parser_superjob(vacancy))

    return vacancy_data


vacancy = 'Python'
vacancies = parser_vacancy(vacancy)

with open('vacancies.json', 'w', encoding='utf-8') as outfile:
    json.dump(vacancies, outfile, ensure_ascii=False)

# Создаём БД Mongo и записываем туда данные из полученного файла vacancies.json

with open('vacancies.json', encoding='utf-8') as f:
    file_data = json.load(f)
jobs.insert_many(file_data)


# производим поиск и выводим на экран вакансии с заработной платой больше 30000.
# так зарплата до 30002 тоже может быть больше 30000 будем выводить данные отвечающие
# требованиям минимальная зп больше 30000 и максимальная больше 30002,
# т.е. если максимальная зп до 30000 это значит человек не может получать больше 30000
# при зп до 30002 если человек может получать 30001 что соответствует критерию больше 30000.

result = jobs.find({'$or':[{'salary_min':{'$gt':30000}},{'salary_max':{'$gt':30002}}]})

for user in result:
    pprint(user)

# Добавляем новые вакансии.

# Получаем обновлённые данные и выгружаем их в файл vacancies2.json.
def _parser_superjob(vacancy):
    vacancy_data = []
    main_link = 'https://russia.superjob.ru'
    link = 'https://www.superjob.ru/vacancy/search/'
    params = {'keywords': vacancy,
              'profession_only': '1',
              'geo[c][0]': '15',
              'geo[c][1]': '1',
              'geo[c][2]': '9',
              'page': '',
              'noGeo': '1'
              }
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

    response = requests.get(main_link + '/vacancy/search/', params=params, headers=headers)
    if response.ok:
       soup = bs(response.text, 'html.parser')
       page_block = soup.find('a', {'class': 'f-test-button-1'})
    if not page_block:
        last_page = 1
    else:
        page_block = page_block.findParent()
        last_page = int(page_block.find_all('a')[-2].getText())

    for page in range(0, last_page + 1):
        params['page'] = page
        response = requests.get(link, params=params, headers=headers)

        if response.ok:
            parsed_response = bs(response.text, 'html.parser')
            vacancy_items = parsed_response.find_all('div', {'class': 'f-test-vacancy-item'})

            for item in vacancy_items:
                vacancy_data.append(_parser_item_superjob(item))

    return vacancy_data

def _parser_item_superjob(item):

        vacancy_data = {}

        # vacancy_name
        vacancy_name = item.find_all('a')
        vacancy_data['vacancy_name'] = vacancy_name[0].getText()

        # salary
        salary = item.find('span', {'class': 'f-test-text-company-item-salary'}).findChild().text
        if salary == 'По договорённости':
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.replace(u'\xa0', ' ').split()
            salary_currency = salary.pop()
            if salary[0] == 'от':
                salary.remove('от')
                salary_min = float(''.join(salary[i] for i in range(len(salary))))
                salary_max = None
            elif salary[0] == 'до':
                salary.remove('до')
                salary_min = None
                salary_max = float(''.join(salary[i] for i in range(len(salary))))
            else:
                salary = ''.join(salary[i] for i in range(len(salary))).split('—')
                salary_min = float(salary[0])
                salary_max = float(salary[1]) if len(salary) > 1 else float(
                    salary[0])
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency

        # link
        vacancy_link = item.find_all('a')
        vacancy_link = vacancy_link[0]['href']
        vacancy_data['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'

        # site
        vacancy_data['site'] = 'www.superjob.ru'

        return vacancy_data


def parser_vacancy(vacancy):
    vacancy_data = []
    vacancy_data.extend(_parser_superjob(vacancy))

    return vacancy_data


vacancy = 'Python'
vacancies = parser_vacancy(vacancy)

with open('vacancies2.json', 'w', encoding='utf-8') as outfile:
    json.dump(vacancies, outfile, ensure_ascii=False)

# удаляем старую коллекцию
db.jobs.drop()

# Создаём БД Mongo и записываем туда данные из полученного файла vacancies2.json

with open('vacancies2.json', encoding='utf-8') as f:
    file_data = json.load(f)
jobs.insert_many(file_data)
