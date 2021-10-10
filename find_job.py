import json
import os
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

# =========================# Setup #=========================#
# Useful parameters

home_url = 'https://www.superjob.ru/'

occupation = 'python'

params = {
    'keywords': occupation,
    'geo[t][0]': '4'
}

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'}

file_name = 'jobs_list.json'

client = MongoClient('127.0.0.1', 27017)

db = client['job_vacancies']

py_dev = db.pyDevOps


# =========================# Functions #=========================#


def process_address(str_element):
    """Get rid of unwanted symbols"""
    return str_element[str_element.index('•') + 2:].replace(u'\xa0', u' ')


def digits_merge(digits):
    """Processing wages"""

    if digits[1] == 0:
        return digits[0] * 1000
    else:
        tmp = [str(digit) for digit in digits]
        a_str = ''.join(tmp)
        return int(a_str)


def split_half(str_list):
    """Split a list into 2 parts"""

    half = len(str_list) // 2
    return str_list[:half], str_list[half:]


def process_wages(raw_data):
    """Working with wages for each vacancy"""

    digits = []
    wage = {
        'min': None,
        'max': None,
        'type': raw_data[-4:-1]
    }
    if raw_data[0] != 'П':
        for char_index in raw_data.split():
            if char_index.isdigit():
                digits.append(int(char_index))
    else:
        wage['type'] = None

    if len(digits) == 2:
        if raw_data[0] == 'о' or raw_data[0].isdigit:
            wage['min'] = digits_merge(digits)
        if raw_data[0] == 'д':
            wage['max'] = digits_merge(digits)
            wage['min'] = None
    elif len(digits) == 4:
        half_a, half_b = split_half(digits)
        wage['min'] = digits_merge(half_a)
        wage['max'] = digits_merge(half_b)

    return wage


def check_file():
    """Check if JSON file exists"""

    file_path = os.getcwd()
    file = file_path + '/' + file_name
    if os.path.isfile(file) and os.access(file, os.R_OK):
        return True
    else:
        return False


def json_processing(list_of_jobs):
    """Write data into a JSON file"""

    f = open(file_name, "a")

    json.dump(list_of_jobs, f, indent=4, ensure_ascii=False)

    f.close()

    # ======================================================#

    # Read from file

    # with open(file_name, 'r') as sample:
    #     for line in sample:
    #         line = json.loads(line.strip())
    #
    # mongodb_processing(line)

    # ======================================================#


def mongodb_processing(json_data):
    py_dev.insert_many(json_data)


def scraping_page(vacancies):
    """Start scrapping data from a web page, storing data into a list"""

    jobs_list = []

    for vacancy in vacancies:
        job = {}
        vacancy_info = vacancy.find('div', attrs={'class': '_1h3Zg _2rfUm _2hCDz _21a7u'})
        job['title'] = vacancy_info.text
        vacancy_payment = vacancy.find('span', attrs={'class': '_1h3Zg _2Wp8I _2rfUm _2hCDz _2ZsgW'}).text.replace(
            u'\xa0', u' ')
        job['wage'] = process_wages(vacancy_payment)
        if vacancy.find("span", {"class": "_1h3Zg _3Fsn4 f-test-text-vacancy-item-company-name e5P5i _2hCDz _2ZsgW _2SvHc"}) is not None:
            job['employer'] = vacancy.find('span', attrs={
                'class': '_1h3Zg _3Fsn4 f-test-text-vacancy-item-company-name e5P5i _2hCDz _2ZsgW _2SvHc'}).text
        else:
            job['employer'] = None

        address = vacancy.find('span', attrs={'_1h3Zg f-test-text-company-item-location e5P5i _2hCDz _2ZsgW'}).text
        job['address'] = process_address(address)
        job['description'] = vacancy.find('span', attrs={'class': '_1h3Zg _38T7m e5P5i _2hCDz _2ZsgW _2SvHc'}).text

        jobs_list.append(job)

    # Store data into JSON file
    # json_processing(jobs_list)

    # Store data into MongoDB
    mongodb_processing(jobs_list)


def start_process(response_link):
    """Open webpage for scrapping"""

    b_soup = BeautifulSoup(response_link.text, 'html.parser')

    vacancies_list = b_soup.find_all('div', attrs={'class': 'Fo44F QiY08 LvoDO'})

    if not response.ok:
        print('Problem with a link')
    elif not vacancies_list:
        print('Problem with tag:\tclass name invalid ')

    print(f'vacancies per page detected:\t{len(vacancies_list)}')

    scraping_page(vacancies_list)


def find_next_btn(next_page_url):
    """Scrapping webpage for next Btn, with text: 'Дальше'"""
    new_response = requests.get(next_page_url)
    b_soup = BeautifulSoup(new_response.text, 'html.parser')
    print("next url title : ", b_soup.find('title').string)

    btn_list = b_soup.find_all("span", {"class": "_1BOkc"})

    for i in btn_list:
        print(i.text)
        if i.text == 'Дальше':
            print(i.text)
        else:
            print(f'{i.text} not found')
    if btn_list[-2].text == 'Дальше':
        return True
    else:
        return False


def click_next_page():
    """Iterate trow web pages"""
    page = 2
    while page != 6:
        next_page = f"https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4&page={page}"
        new_responce = requests.get(next_page)
        start_process(new_responce)
        print(next_page)
        page += 1


# =========================# Process #=========================#

# Get response
response = requests.get(home_url + 'vacancy/search/', params=params, headers=headers)

# Start scrapping data from webpage
start_process(response)

# Collect data from next 5 pages
click_next_page()

# Check MongoDB Content
for doc in py_dev.find({}):
    pprint(doc)
