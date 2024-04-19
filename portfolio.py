#!/usr/bin/env python3
# 
# depends on requests 
# "pip install requests"

import os
import json
import sqlite3

import requests

db_file = os.path.expanduser('~/.portfolio.db')

# Define a function to create or connect to the database
def create_or_connect_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    create_table = """CREATE TABLE IF NOT EXISTS portfolio (
        'date' datetime not null primary key default current_timestamp,
        'cents' integer not null,
        'amount' real not null,
        'code' char(3) not null,
        'coin' varchar(15) not null,
        'remarks' varchar(150) not null
    );"""
    cursor.execute(create_table)
    conn.commit()
    return conn, cursor

# Define a function to fetch portfolio data from the database
def fetch_portfolio_data(cursor):
    cursor.execute("""
        SELECT
            coin,
            sum(cents)/100.00 as euro,
            sum(sum(cents)) over()/100.0 as total_eur,
            round(100.0*sum(cents) / sum(sum(cents)) over(), 2) as per,
            sum(amount),
            code,
            round(sum(cents)/sum(amount)/100, 2) as price
        FROM portfolio 
        GROUP BY code 
        HAVING euro > 0
        ORDER BY sum(cents) desc;
    """)
    return cursor.fetchall()

# TOR
def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

# Define a function to fetch coin prices
def fetch_coin_prices(session, coin_codes):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(coin_codes)}&vs_currencies=btc,eur,usd"
    response = session.get(url)
    return json.loads(response.text)

def main():
    conn, cursor = create_or_connect_db(db_file)
    all_coins = fetch_portfolio_data(cursor)
    conn.close()

    session = get_tor_session()
    coin_codes = [row[0] for row in all_coins]
    
    t_total = t_profit = t_btc = 0

    # Fetch coin prices
    prices = fetch_coin_prices(session, coin_codes)

    # Print the table headers
    print("{:<20}  {:<14}  {:<8}  {:<30}  {:<21}  {:<19}".format(
    "balance", "invest €     %", "entry  €    !x → €", "price  €         $            !x", "total   €           ₿", "profit  €      %"))
    print("{:<20}  {:<14}  {:<18}  {:<30}  {:<21}  {:<19}".format(
    "--------------------", "--------------", "------------------", "--------------------------------", "---------------------", "----------------"))

    for row in all_coins:
        coin_code = row[0]
        t_invest = round(row[2], 2)
        coin_prices = prices[coin_code]

        price_eur = round(coin_prices['eur'], 2)
        price_usd = round(coin_prices['usd'], 2)
        price_btc = round(coin_prices['btc'], 8)

        total = price_eur * row[4]
        t_total += total
        profit = total - row[1]
        t_profit += profit
        profit_per = profit * 100.0 / row[1]
        total_btc = price_btc * row[4]
        t_btc += total_btc

        row = list(row)
        row.pop(2)
        row.extend([price_eur, total, profit, profit_per, price_usd, price_btc, total_btc])
                
        my_price_oposite = row[5]/price_btc 
        price_oposite = price_btc
        if row[0] == "bitcoin":
            my_price_oposite = row[5]*prices['monero']['btc']
            price_oposite = round(1/prices['monero']['btc'], 8)


        print("{:<15}  {:>3}  {:>8.2f}  {:>4.1f}  {:>8.2f}  {:>8.2f}  {:>8.2f}  {:>8.2f}  {:>12.8f}  {:>9.2f}  {:>10.8f}  {:>9.2f}  {:>5.1f}".format(
            row[3], row[4], row[1], row[2], row[5], my_price_oposite, row[6], price_usd, price_oposite, total, total_btc, profit, profit_per))
        

    # Print the table footer (TOTALS)
    print("{:<20}  {:<14}  {:<18}  {:<30}  {:<21}  {:<19}".format(
    "--------------------", "--------------", "------------------", "--------------------------------", "---------------------", "----------------"))
    print("{:<20}  {:>8.2f}  {:>4}  {:<20}  {:<30}  {:>9.2f}  {:>10.8f}  {:>9.2f}  {:>5.1f}".format(
        "", t_invest, "", round(t_invest/t_btc, 2), "", round(t_total, 2), round(t_btc, 8), round(t_profit, 2), round(t_profit * 100 / t_invest, 2)))

if __name__ == "__main__":
    main()
