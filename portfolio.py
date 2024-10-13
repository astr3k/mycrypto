#!/usr/bin/env python3
# 

import json
import os
import sqlite3
import requests

db_file = os.path.expanduser('~/.portfolio.db')

def create_or_connect_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    create_table = """CREATE TABLE IF NOT EXISTS portfolio (
        'date' datetime not null primary key default current_timestamp,
        'cents' integer not null,
        'amount' real not null,
        'code' char(3) not null,
        'remarks' varchar(150) not null
    );"""
    cursor.execute(create_table)
    conn.commit()
    return conn, cursor

def fetch_portfolio_data(cursor):
    cursor.execute("""
        SELECT
            code,
            sum(cents)/100.00 as euro,
            sum(sum(cents)) over()/100.0 as total_eur,
            round(100.0*sum(cents) / sum(sum(cents)) over(), 2) as per,
            sum(amount),
            round(sum(cents)/sum(amount)/100, 2) as price
        FROM portfolio 
        GROUP BY code 
        HAVING euro > 0;
    """)
    rows = cursor.fetchall()
    return rows

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

def fetch_coin_prices(session):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,monero&vs_currencies=usd,eur,btc"
    response = session.get(url)
    prices_dict = json.loads(response.text)
    prices_list = [tuple(prices_dict["bitcoin"].values()), tuple(prices_dict["monero"].values())]
    return prices_list

def main():
    conn, cursor = create_or_connect_db(db_file)
    session = get_tor_session()
    port = fetch_portfolio_data(cursor)
    conn.close()
    price = fetch_coin_prices(session)

    print("{:<14}  {:<16}  {:<29}  {:<31}  {:<16}".format(
    "inv€st       %", "€ntry  ₿     XMR", "₿alance                   XMR", "pric€              $   !BTC/XMR", "total   €      %"))
    print("{:-<14}  {:-<16}  {:-<29}  {:-<31}  {:-<16}".format('-', '-', '-', '-', '-'))
    # body
    # BTC
    print("{:>8.2f}  {:>4.1f}  \033[1m{:>8.2f}\033[0m  {:>6.2f}  \033[1m{:>^10.8f}\033[0m  {:>17.12f}  {:>9.2f}  {:>9.2f}  {:>9.5f}  {:>9.2f}  {:>5.1f}".format( 
        port[0][1],                                                                                                 # 0 invest    €
        port[0][3],                                                                                                 # 1 invest    %
        port[0][5],                                                                                                 # 2 entry     BTC
        port[0][5] * price[1][2],                                                                                   # 3 entry     XMR
        port[0][4],                                                                                                 # 4 balance   BTC
        port[0][4] / price[1][2],                                                                                   # 5 balance   XMR
        price[0][1],                                                                                                # 6 price     €    
        price[0][0],                                                                                                # 7 price     $
        price[0][2] / price[1][2],                                                                                  # 8 price     !x
        port[0][4] * price[0][1],                                                                                   # 9 balance   €
        (port[0][4] * price[0][1] - port[0][1]) / port[0][1] * 100))                                                #10 profit    %

    # XMR
    print("{:>8.2f}  {:>4.1f}  {:>8.2f}  \033[1m{:>6.2f}\033[0m  {:>10.8f}  \033[1m{:>17.12f}\033[0m  {:>9.2f}  {:>9.2f}  {:>9.5f}  {:>9.2f}  {:>5.1f}".format(           
        port[1][1],                                                                                                 # 0 inv€st    €
        port[1][3],                                                                                                 # 1 inv€st    %
        port[1][5] / price[1][2],                                                                                   # 2 €ntry     ₿
        port[1][5],                                                                                                 # 3 €ntry     XMR
        port[1][4] * price[1][2],                                                                                   # 4 ₿alance   ₿
        port[1][4],                                                                                                 # 5 ₿alance   XMR
        price[1][1],                                                                                                # 6 pric€     €
        price[1][0],                                                                                                # 7 pric€     $
        price[1][2] / price[0][2],                                                                                  # 8 pric€     !x
        port[1][4] * price[1][1],                                                                                   # 9 total     €
        (port[1][4] * price[1][1] - port[1][1]) / port[1][1] * 100))                                                #10 total     %

    # footer totals
    print("{:-<14}  {:-<16}  {:-<29}  {:-<31}  {:-<16}".format('-', '-', '-', '-', '-'))
    print("{:>8.2f}  {:<4}  {:>8.2f}  {:>6.2f}  {:>10.8f}  {:>17.12f}  {:>31}  {:>9.2f}  {:>5.1f}".format(           
        port[1][2],                                                                                                 # 0 invest    €
        "",                                                                                                         # 1
        port[1][2] / (port[0][4] + port[1][4] * price[1][2]),                                                       # 2 entry     BTC
        port[1][2] / (port[0][4] / price[1][2] + port[1][4]),                                                       # 3 entry     XMR
        port[0][4] + port[1][4] * price[1][2],                                                                      # 4 balance   BTC
        port[0][4] / price[1][2] + port[1][4],                                                                      # 5 balance   XMR
        "",                                                                                                         # 6
        port[0][4] * price[0][1] + port[1][4] * price[1][1],                                                        # 7 balance   €
        ((port[0][4] * price[0][1] - port[0][1]) + (port[1][4] * price[1][1] - port[1][1])) / port[1][2] * 100))    # 8 profit    %

if __name__ == "__main__":
    main()
