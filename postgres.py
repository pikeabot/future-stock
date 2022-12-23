import csv
import psycopg2
import selenium
import urllib3
from bs4 import BeautifulSoup
from utils import get_formatted_date
#
# FILENAMES = ['COIN', 'TSLA', 'QQQ', 'ENPH', 'REGN', 'NFLX', 'SNOW', 'AAPL', 'GME', 'C', 'JPM', 'XOM', 'OXY',
#              'GOOGL', 'UPST','AMZN', 'DIS', 'BAC', 'TWTR', 'DASH', 'AMC', 'USO', 'GLD', 'MOS', 'LMT', 'PTON',
#              'AFRM', 'META', 'F']

FILENAMES = ['TSLA']
def update_stock_from_csv(filename):
    filepath = f'/Users/jocelynchang/Documents/data/{filename}.csv'
    table_sql = f'CREATE TABLE IF NOT EXISTS public.{filename.lower()} ' \
                f'(date date NOT NULL, close money NOT NULL, volume integer NOT NULL, ' \
                f'open money NOT NULL, high money NOT NULL, low money NOT NULL, ' \
                f'CONSTRAINT "{filename}_pkey" PRIMARY KEY (date)) ' \
                f'TABLESPACE pg_default; ' \
                f'ALTER TABLE IF EXISTS public.{filename.lower()} ' \
                f'OWNER to postgres;'

    sql = f'INSERT INTO {filename.lower()} (date, close, volume, open, high, low) VALUES (%s, %s, %s, %s, %s, %s);'
    conn = None
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect("dbname=stonks user=postgres password=bonitis")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute(table_sql, ())
        with open(filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    # execute the INSERT statement
                    formatted_date = get_formatted_date(row[0])
                    if row[2] == 'N/A':
                        volume = '0'
                    else:
                        volume = row[2].replace(',', '')
                    cur.execute(sql, (formatted_date, row[1], volume, row[3], row[4], row[5]))
                    # commit the changes to the database
                    conn.commit()
                    line_count += 1
        cur.close()
        # print(f'Processed {line_count} lines.')
        print(f'Finished processing {filename}')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:

            conn.close()

def update_stock_tables_from_csv():
    for filename in FILENAMES:
        update_stock_from_csv(filename)

def update_beautiful_spy():
    """
    <tr class="historical-data__row">
    <th scope="row" class="historical-data__cell">10/06/2022</th>
    <td scope="row" class="historical-data__cell">373.2</td>
    <td scope="row" class="historical-data__cell">82,333,540</td>
    <td scope="row" class="historical-data__cell">375.62</td>
    <td scope="row" class="historical-data__cell">378.72</td>
    <td scope="row" class="historical-data__cell">372.68</td></tr>
    :return:
    """
    # url = 'https://www.nasdaq.com/market-activity/funds-and-etfs/spy/historical'
    url = 'https://www.nasdaq.com/market-activity/funds-and-etfs/'
    http = urllib3.PoolManager()
    print(f'SENDING REQUEST')
    resp = http.request('GET', url)
    # page = resp.data
    print(resp.status)
    # with open(page) as fp:
    #     soup = BeautifulSoup(fp, 'html.parser')
    #
    # tag = soup.b
    # print(tag['historical-data__row'])

def update_selenium_spy():
    from selenium.webdriver.chrome.service import Service
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    url = 'https://www.nasdaq.com/market-activity/funds-and-etfs/spy/historical'

    service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service)
    # driver = webdriver.Firefox(executable_path="/path/to/geckodrive.exe")
    driver.get(url)

    rows = driver.find_elements(By.XPATH, "//tr[@class='historical-data__row']") 
    return rows


# update_spy_from_csv()
update_selenium_spy()
# update_stock_tables_from_csv()
# update_stock_from_csv('DASH')
# update_stock_from_csv('IWM')

