import urllib.request, json, sqlite3
from urllib.request import Request, urlopen
from tabulate import tabulate
 
# connect and/or create database;
create_table = """ create table if not exists crypto (
            'date' datetime not null primary key default current_timestamp,
            'cents' integeer not null,
            'amount' real not null,
            'code' char(3) not null,
            'coin' varchar(15) not null,
            'remarks' varchar(150) not null
        ); """

try:
    conn = sqlite3.connect('crypto.db')
    cursor = conn.cursor()
    cursor.execute(create_table)

except sqlite3.Error as error:
    print('Error occured - ', error)

finally:
    if conn:
        conn.close()

try:
    conn = sqlite3.connect('crypto.db')
    cursor = conn.cursor()
    cursor.execute("select coin, sum(cents)/100.00 as euro, sum(sum(cents)) over()/100.0 as total_eur, round(100.0*sum(cents) / sum(sum(cents)) over(), 2) as per, sum(amount), code, round(sum(cents)/sum(amount)/100, 2) as price FROM crypto group by code order by sum(cents) desc;")
    all_coins = cursor.fetchall()
    cursor.close()


except sqlite3.Error as error:
    print('Error occured - ', error)

finally:
    if conn:
        conn.close()


# PRINT TABLE
tablaa = [("invest", "%", "amount", "code", "avg price €", "price €", "total €", "profit €", "profit %", "price ₿", "total ₿", "price €/₿")]
t_total = t_profit = t_btc = 0
for row in all_coins:
    rowl = list(row)
    # GET PRICES
    url = "https://api.coingecko.com/api/v3/simple/price?ids="+rowl[0]+"&vs_currencies=eur,btc"
    request_url = Request(url, headers={"User-Agent": "Mozilla/5.0"})
 
    try:
        with urllib.request.urlopen(request_url) as u:
            price = json.loads(u.read().decode())

    except urllib.Error as error:
        print('Error occured - ', error)
    
    
    t_invest = round(rowl[2], 2)
    rowl.pop(2)
    price_eur = round(price[row[0]]['eur'], 2)
    total = price[row[0]]['eur']*row[4]
    t_total = t_total + total
    profit = total - row[1] 
    t_profit = t_profit + total - row[1]
    profit_per = profit * 100.0 / row[1]
    price_btc = round(price[row[0]]['btc'], 8)
    total_btc = price_btc * row[4]
    t_btc = t_btc + total_btc
    price_eur_btc = round(row[1] / total_btc, 2)
    
    rowl.extend([ price_eur, total, profit, profit_per, price_btc, total_btc, price_eur_btc ])    
    tablaa.append(rowl)
tablaa.append(("", float(t_invest), "", "", "", "", "", t_total, t_profit,t_profit * 100 / t_invest, "", t_btc, t_invest / t_btc))
print(tabulate(tablaa, headers=("firstrow"), floatfmt="0.2f"))

