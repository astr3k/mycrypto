# pip install requests[socks] stem tabulate
# python3 -m pip install --upgrade pip
# https://stackoverflow.com/questions/30286293/make-requests-using-python-over-tor

import json, sqlite3, requests
from tabulate import tabulate

##TOR
def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

session = get_tor_session()

#from stem import Signal
#from stem.control import Controller

#with Controller.from_port(port = 9051) as controller:
#    controller.authenticate(password='your password set for tor controller port in torrc')
#    print("Success!")
#    controller.signal(Signal.NEWNYM)
#    print("New Tor connection processed")


# connect and/or create database;
create_table = """ CREATE TABLE IF NOT EXISTS portfolio (
            'date' datetime not null primary key default current_timestamp,
            'cents' integeer not null,
            'amount' real not null,
            'code' char(3) not null,
            'coin' varchar(15) not null,
            'remarks' varchar(150) not null
        ); """

try:
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    cursor.execute(create_table)

except sqlite3.error as error:
    print('Error occured - ', error)

finally:
    if conn:
        conn.close()

try:
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    cursor.execute(""" SELECT
                        coin,
                        sum(cents)/100.00 as euro,
                        sum(sum(cents)) over()/100.0 as total_eur,
                        round(100.0*sum(cents) / sum(sum(cents)) over(), 2) as per,
                        sum(amount),
                        code,
                        round(sum(cents)/sum(amount)/100, 2) as price
                    FROM portfolio GROUP BY code ORDER BY sum(cents) desc; """)
    all_coins = cursor.fetchall()
    cursor.close()


except sqlite3.error as error:
    print('Error occured - ', error)

finally:
    if conn:
        conn.close()


# PRINT TABLE
tablaa = [("invest", "%", "amount", "code", "avg price €", "price €", "total €", "profit €", "profit %", "price USD", "price ₿", "total ₿", "price $/₿", "price €/₿")]
t_total = t_profit = t_btc = 0
for row in all_coins:
    rowl = list(row)
    
    # GET PRICES
    
    url = "https://api.coingecko.com/api/v3/simple/price?ids=usd,"+rowl[0]+"&vs_currencies=btc,eur,usd"
    p = session.get(url).text
    price = json.loads(p)

    t_invest = round(rowl[2], 2)
    rowl.pop(2)
    price_btc = round(price[row[0]]['btc'], 8)
    price_eur = round(price[row[0]]['eur'], 2)
    price_usd = round(price[row[0]]['usd'], 2)
    usd_eur = round(price['usd']['eur'], 6)
    total = price[row[0]]['eur']*row[4]
    t_total = t_total + total
    profit = total - row[1] 
    t_profit = t_profit + total - row[1]
    profit_per = profit * 100.0 / row[1]
    total_btc = price_btc * row[4]
    t_btc = t_btc + total_btc
    price_eur_btc = round(row[1] / total_btc, 2)
    price_usd_btc = round(price_eur_btc / usd_eur, 2)
    
    rowl.extend([ price_eur, total, profit, profit_per, price_usd, price_btc, total_btc, price_usd_btc, price_eur_btc ])    
    tablaa.append(rowl)
tablaa.append(("", float(t_invest), "", "", "", "", "", t_total, t_profit,t_profit * 100 / t_invest, "", "", t_btc, (t_invest / t_btc) / usd_eur, t_invest / t_btc))
print(tabulate(tablaa, headers=("firstrow"), floatfmt="0.2f"))

