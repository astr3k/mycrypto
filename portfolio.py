import json
import sqlite3
import subprocess

# Package name you want to install
package_name = "requests"

# Check if the package is already installed
try:
    import importlib
    importlib.import_module(package_name)
    #print(f"{package_name} is already installed.")
except ImportError:
    # Use subprocess to run the pip install command
    try:
        subprocess.check_call(["pip", "install", package_name])
        print(f"Successfully installed {package_name}.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing {package_name}: {e}")

import requests


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
        FROM portfolio GROUP BY code ORDER BY sum(cents) desc;
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
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=usd,{','.join(coin_codes)}&vs_currencies=btc,eur,usd"
    response = session.get(url)
    return json.loads(response.text)

def main():
    conn, cursor = create_or_connect_db('portfolio.db')
    all_coins = fetch_portfolio_data(cursor)
    conn.close()

    session = get_tor_session()
    coin_codes = [row[0] for row in all_coins]

    # Fetch coin prices
    prices = fetch_coin_prices(session, coin_codes)

    # Print the table headers
    print("{:<7}  {:<15}  {:<20}  {:<8}  {:<52}  {:<21}  {:<19}".format(
    "", "invest €      %", "amount", "entry  €", "price  €         $           ₿        €/₿        $/₿", "total    €          ₿", "profit  €       %"))
    print("{:<7}  {:<15}  {:<20}  {:<8}  {:<52}  {:<21}  {:<19}".format(
    "-------", "---------------", "--------------------", "--------", "----------------------------------------------------", "---------------------", "-----------------"))
    
    t_total = t_profit = t_btc = 0

    for row in all_coins:
        coin_code = row[0]
        t_invest = round(row[2], 2)
        coin_prices = prices[coin_code]

        price_btc = round(coin_prices['btc'], 8)
        price_eur = round(coin_prices['eur'], 2)
        price_usd = round(coin_prices['usd'], 2)

        usd_eur = round(prices['usd']['eur'], 6)
        total = price_eur * row[4]
        t_total += total
        profit = total - row[1]
        t_profit += profit
        profit_per = profit * 100.0 / row[1]
        total_btc = price_btc * row[4]
        t_btc += total_btc
        price_eur_btc = round(row[1] / total_btc, 2)
        price_usd_btc = round(price_eur_btc / usd_eur, 2)

        row = list(row)
        row.pop(2)
        row.extend([price_eur, total, profit, profit_per, price_usd, price_btc, total_btc, price_usd_btc, price_eur_btc])
    
        print("{:<7}  {:>8.2f}  {:>5.2f}  {:<15}  {:>3}  {:>8.2f}  {:>8.2f}  {:>8.2f}  {:>10.8f}  {:>9.2f}  {:>9.2f}  {:>9.2f}  {:>10.8f}  {:>9.2f}  {:>6.2f}".format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], price_usd, price_btc, price_eur_btc, price_usd_btc, total, total_btc, profit, profit_per))
    
    # Print the table footer (TOTALS)
    print("{:<7}  {:<15}  {:<20}  {:<8}  {:<52}  {:<21}  {:<19}".format(
    "-------", "---------------", "--------------------", "--------", "----------------------------------------------------", "---------------------", "-----------------"))
    print("{:<7}  {:>8.2f}  {:>5}  {:<20}  {:<8}  {:<8}  {:<8}  {:<10}  {:>9.2f}  {:>9.2f}  {:>9.2f}  {:>10.8f}  {:>9.2f}  {:>6.2f}".format(
        "", t_invest, "", "", "", "", "", "", round(t_invest / t_btc, 2), round((t_invest / t_btc) / usd_eur, 2),  round(t_total, 2), round(t_btc, 8), round(t_profit, 2), round(t_profit * 100 / t_invest, 2)))

if __name__ == "__main__":
    main()
