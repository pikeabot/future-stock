import csv
import psycopg2
from decimal import Decimal
from utils import convert_currency_to_float, get_date_strikeprice_from_option, get_formatted_date


FILENAMES = ['COIN', 'TSLA', 'QQQ', 'ENPH', 'REGN', 'NFLX', 'SNOW', 'AAPL', 'GME', 'C', 'JPM', 'XOM', 'OXY',
             'GOOGL', 'UPST','AMZN', 'DIS', 'BAC', 'TWTR', 'DASH', 'AMC', 'USO', 'GLD', 'MOS', 'LMT', 'PTON',
             'AFRM', 'META', 'F', 'SPY']


def get_closing_stock_prices():
    full_filename = f'/Users/jocelynchang/Documents/Stonks_Research/hold_to_expiration.csv'
    conn = None
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect("dbname=stonks user=postgres password=bonitis")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        rows = []
        with open(full_filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    rows.append(row)
                    line_count += 1
                else:
                    try:
                        # execute the INSERT statement
                        ticker = row[0]
                        sql = f'SELECT * FROM public.{ticker.lower()} WHERE CAST(date AS DATE) = %s;'
                        # print(f'SQL :{sql}')
                        formatted_date, strikeprice, is_call, is_spread, strikeprice_delta = get_date_strikeprice_from_option(row[2])
                        cur.execute(sql, (formatted_date, ))
                        data = cur.fetchall()
                        row.pop()
                        row.pop()
                        close = convert_currency_to_float(data[0][1])
                        row.append(str(close))
                        if is_spread:
                            buy_price = convert_currency_to_float(data[0][4])
                            if close >= Decimal(strikeprice):
                                if is_call:
                                    profit = strikeprice_delta - buy_price
                                else:
                                    profit = Decimal(0)
                            else:
                                if is_call:
                                    profit = Decimal(0)
                                else:
                                    profit = strikeprice_delta - buy_price
                        else:
                            profit = close - Decimal(strikeprice)
                            if not is_call:
                                profit = profit * Decimal(-1)
                        row.append(str(profit))
                        rows.append(row)
                        line_count += 1
                    except Exception as e:
                        print(f'ERROR: {e}')
        cur.close()
        # print(rows)

        results_filename = f'/Users/jocelynchang/Documents/Stonks_Research/hold_to_expiration_results.csv'
        print(f'NUM OF ROWS: {len(rows)}')
        with open(results_filename, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f'Processed {line_count} lines.')
        print(f'Finished processing {full_filename}')
        print(f'Finished writing to {results_filename}')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:

            conn.close()

get_closing_stock_prices()
