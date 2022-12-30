import json
import psycopg2

from flask import Flask
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

from utils import get_formatted_date, scrape_for_stock_data

app = Flask(__name__)

CME_HISTORICAL_DATA_URL = 'https://www.nasdaq.com/market-activity/funds-and-etfs/{}/historical'
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/stock_data/<ticker>")
def get_stock_data_for_ticker(ticker):
    """
    Scrape the CME website for 1 month of data for a desired stock
    :param ticker: The CME symbol for a given stock ticker
    :return: json of data which includes [date, close/last, volume, open, high, low]
    """
    rows = scrape_for_stock_data(CME_HISTORICAL_DATA_URL.format(ticker), "//tr[@class='historical-data__row']")
    rows_text = []
    for row in rows:
        rows_text.append(row.text)
    return json.dumps(rows_text)

@app.route("/fed-schedule")
def get_fed_schedule():
    pass

@app.route("/stock_data/<ticker>/update")
def update_ticker_postgres(ticker):
    table_sql = f'CREATE TABLE IF NOT EXISTS public.{ticker.lower()} ' \
                f'(date date NOT NULL, close money NOT NULL, volume integer NOT NULL, ' \
                f'open money NOT NULL, high money NOT NULL, low money NOT NULL, ' \
                f'CONSTRAINT "{ticker}_pkey" PRIMARY KEY (date)) ' \
                f'TABLESPACE pg_default; ' \
                f'ALTER TABLE IF EXISTS public.{ticker.lower()} ' \
                f'OWNER to postgres;'

    sql1 = f'INSERT INTO {ticker.lower()} (date, close, volume, open, high, low) VALUES (%s, %s, %s, %s, %s, %s) '
    sql2 = f'ON CONFLICT DO NOTHING;'
    sql = sql1 + sql2
    try:
        # Get data
        rows = scrape_for_stock_data(CME_HISTORICAL_DATA_URL.format(ticker), "//tr[@class='historical-data__row']")

        # Connect to your postgres DB
        conn = psycopg2.connect("dbname=stonks user=postgres password=bonitis")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute(table_sql, ())
        # execute the INSERT statement
        for row in rows:
            r = row.text.split(' ')
            formatted_date = get_formatted_date(r[0])
            if r[2] == 'N/A':
                volume = '0'
            else:
                volume = r[2].replace(',', '')
            cur.execute(sql, (formatted_date, r[1], volume, r[3], r[4], r[5]))
        # commit the changes to the database
        conn.commit()
        return f'Finished updating {ticker.upper()}'
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return error
