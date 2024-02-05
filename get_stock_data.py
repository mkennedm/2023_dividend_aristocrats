import csv
import requests

def get_dividends(stock):
    headers = {
        'Content-Type': 'application/json'
    }
    startDate = '1999-01-04'
    token = get_api_token('tiingo_api_token.txt')
    requestResponse = requests.get(f"https://api.tiingo.com/tiingo/daily/{stock}/prices?startDate={startDate}&token={token}", headers=headers)
    return requestResponse.json()

def get_api_token(filename):
    token = ''

    with open(filename, 'r') as file:
        token = file.readline().strip()
    return token

def get_stocks_list(filename):
    stocks = []

    with open(filename, 'r') as file:
        for line in file:
            stocks.append(line.strip())
    return stocks

def create_rows(symbol):
    dividend_data = get_dividends(symbol)
    rows = []
    
    for day in dividend_data:
        if day['divCash']:
            row = {'date': day['date'],
                   'symbol': symbol,
                   'dividend': day['divCash']}
            rows.append(row)
    return rows

def store_dividend_data(dividend_stocks_file, output_file='dividends_data.csv'):
    symbols = get_stocks_list(dividend_stocks_file)

    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['date', 'symbol', 'dividend']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for symbol in symbols:
            rows = create_rows(symbol)
            for row in rows:
                writer.writerow(row)

    return


    
