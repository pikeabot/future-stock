import json

from flask import Flask
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

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
    service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service)
    # driver = webdriver.Firefox(executable_path="/path/to/geckodrive.exe")
    driver.get(CME_HISTORICAL_DATA_URL.format(ticker))

    rows = driver.find_elements(By.XPATH, "//tr[@class='historical-data__row']")
    rows_text = []
    for row in rows:
        rows_text.append(row.text)
    return json.dumps(rows_text)

@app.route("/fed-schedule")
def get_fed_schedule():
    pass

@app.route("/update/<ticker>")
def update_ticker():
    pass
