import json
from re import sub
from decimal import Decimal

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_formatted_date(unformatted_date):
    """
    Convert date fom MM/DD/YYYY to postgres date format YYYY-MM-DD
    :param unformatted_date:
    :return:
    """
    d = unformatted_date.split('/')
    year = d[2]
    month = d[0]
    day = d[1]
    if len(year) < 4:
        year = '20' + year
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    return f'{year}-{month}-{day}'

def get_date_strikeprice_from_option(date_str):
    split_str = date_str.split(' ')
    formatted_date = get_formatted_date(split_str[0].strip())

    # print(f'FORMATTED DATE: {formatted_date}')
    is_call = split_str[1][-1] == 'C'
    # print(f'IS CALL: {is_call}')
    raw_strikeprice_str = split_str[1][:-1]
    # print(f'RAW STRIKEPRICE: {raw_strikeprice_str}')
    is_spread = False
    strikeprice_delta = 0
    if '/' in raw_strikeprice_str:
        is_spread = True
        strikeprices = raw_strikeprice_str.split('/')
        strikeprice = strikeprices[1].strip()
        strikeprice_delta = Decimal(strikeprice) - Decimal(strikeprices[0].strip())
    else:
        strikeprice = raw_strikeprice_str.strip()

    return formatted_date, strikeprice, is_call, is_spread, strikeprice_delta

def convert_currency_to_float(money):
    return Decimal(sub(r'[^\d.]', '', money))

def scrape_for_stock_data(url, tag_string):
    """
    Get data from website via selenium
    :param url: url of site to be scraped
    :param tag_string: string with desired tag info ex. "//tr[@class='historical-data__row']"
    :return:
    """
    service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service)
    # driver = webdriver.Firefox(executable_path="/path/to/geckodrive.exe")
    driver.get(url)

    rows = driver.find_elements(By.XPATH, tag_string)
    return rows
