import urllib.request, json, sqlite3
from tabulate import tabulate

# connect and/or create database;
table = """ create table if not exists crypto (
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
    cursor.execute(table)

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
tablaa = [("invest", "%", "amount", "code", "avg price €", "price €", "total €", "profit €", "price ₿")]
t_total = t_profit = 0
for row in all_coins:
    rowl = list(row)
    # GET PRICES
    
    url = "https://api.coingecko.com/api/v3/simple/price?ids="+rowl[0]+"&vs_currencies=eur%2Cbtc"
    try:
        with urllib.request.urlopen(url) as u:
            price = json.loads(u.read().decode())

    except urllib.Error as error:
        print('Error occured - ', error)
    
    t_invest = round(rowl[2], 2)
    rowl.pop(2)
    rowl.append(price[row[0]]['eur'])
    total = price[row[0]]['eur']*row[4]
    rowl.append(total)
    t_total = t_total + total
    rowl.append(total-row[1])
    t_profit = t_profit + total - row[1]
    rowl.append(round(price[row[0]]['btc'], 8))
    tablaa.append(rowl)
tablaa.append(("", float(t_invest),100,"","",0,0,t_total,t_profit,""))
print(tabulate(tablaa, headers=("firstrow"), floatfmt="0.2f"))

