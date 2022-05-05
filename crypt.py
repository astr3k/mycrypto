import urllib.request, json, sqlite3
from decimal import Decimal, ROUND_05UP, ROUND_HALF_UP
from tabulate import tabulate

# connect and/or create database;
table = """ create table if not exists 'crypt' (
            'date' datetime primary key default current_timestamp,
            'euro' decimal(12,2) not null,
            'crypto' char(3) not null,
            'market' varchar(150) not null
        ); """

try:
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute(table)

except sqlite3.Error as error:
    print('Error occured - ', error)

finally:
    if conn:
        conn.close()

try:
    conn = sqlite3.connect('crypt.db')
    cursor = conn.cursor()
    cursor.execute('select sum(euro), sum(btc) from bitcoin')
    btc = cursor.fetchall()
    cursor.execute('select sum(euro), sum(xmr) from monero')
    xmr = cursor.fetchall()
    cursor.execute('select sum(euro), sum(ada) from cardano')
    ada = cursor.fetchall()
    cursor.close()

except sqlite3.Error as error:
    print('Error occured - ', error)

finally:
    if conn:
        conn.close()


# GET PRICES
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Ccardano%2Cmonero&vs_currencies=eur%2Cusd%2Cbtc"
try: 
    with urllib.request.urlopen(url) as u:
        price = json.loads(u.read().decode())

except urllib.Error as error:
    print('Error occured - ', error)


# Formating data
t_btc = round(btc[0][1], 8)
t_xmr = round(xmr[0][1], 10)
t_ada = round(ada[0][1], 6)
t_inv =  btc[0][0]+xmr[0][0]+ada[0][0]
i_btc_per = round(100.0*btc[0][0]/t_inv, 2)
i_xmr_per = round(100.0*xmr[0][0]/t_inv, 2)
i_ada_per = round(100.0*ada[0][0]/t_inv, 2)

ap_btc = round(float(btc[0][0]/t_btc), 2) 
ap_xmr = round(float(xmr[0][0]/t_xmr), 2) 
ap_ada = round(float(ada[0][0]/t_ada), 2) 

p_btc = round(float(price['bitcoin']['eur']), 2)
p_xmr = round(float(price['monero']['eur']), 2)
p_ada = round(float(price['cardano']['eur']), 2)
pb_btc = round(price['bitcoin']['btc'], 8)
pb_xmr = round(price['monero']['btc'], 8)
pb_ada = round(price['cardano']['btc'], 8)
t_e_btc = p_btc * t_btc
t_e_xmr = p_xmr * t_xmr
t_e_ada = p_ada * t_ada
total_e = t_e_btc + t_e_xmr + t_e_ada
t_b_btc = round(pb_btc * t_btc, 8)
t_b_xmr = round(pb_xmr * t_xmr, 8)
t_b_ada = round(pb_ada * t_ada, 8)
total_b = round(t_b_btc + t_b_xmr + t_b_ada, 8)

# PRINT TABLE
Table = [[              "amount",   "invest",   "%",        "avg price €",  "price €",  "price ₿",  "total ₿",  "total €",  "profit €" ],
        [   "bct",      t_btc,      btc[0][0],  i_btc_per,  ap_btc,         p_btc,      pb_btc,     t_b_btc,    t_e_btc,    t_e_btc-btc[0][0]],
        [   "xmr",      t_xmr,      xmr[0][0],  i_xmr_per,  ap_xmr,         p_xmr,      pb_xmr,     t_b_xmr,    t_e_xmr,    t_e_xmr-xmr[0][0]],
        [   "ada",      t_ada,      ada[0][0],  i_ada_per,  ap_ada,         p_ada,      pb_ada,     t_b_ada,    t_e_ada,    t_e_ada-ada[0][0]],
        [   "TOTAL",    "",         t_inv,      "",         "",             "",         "",         total_b,    total_e,    total_e-t_inv]]

print(tabulate(Table, headers=("firstrow"), floatfmt="0.2f", colalign=("left", "left", "right", "right", "right", "right",)))
