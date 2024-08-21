import requests
import hashlib
import time
import datetime
import json
import pandas as pd
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")
key = config.get("PARSER", "api_key")
path = config.get("PARSER", "path")

def get_token(seller_id, api_key):
    timestamp = int(time.time())
    data = api_key + str(timestamp)
    sign = hashlib.sha256(data.encode('utf-8')).hexdigest()
    json = {
        "seller_id": seller_id,
        "timestamp": timestamp,
        "sign": sign
    }
    url = 'https://api.digiseller.ru/api/apilogin'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.post(url, json=json, headers=headers)
    if r.status_code != 200:
        return None
    res = r.json()
    if res['retval'] != 0:
        return None
    return res['token']

id_list = []
amount_list = []
name_list_a = []
amount_list_a = []
sell = []

file = open(path, 'r')
for line in file:
    id_list.append(int(line.strip().split("/")[-1]))
file.close()
#print(id_list)



name_list = []

def get_data():
    t = get_token("1122744", "DB7EC97A4A634946B6C06D020C3630D8")
    url = f"https://api.digiseller.ru/api/rekl?owner=1&token={t}"
    r = requests.get(url=url)
    products = r.json()
    for product in products["products"]:
        if product["id"] in id_list:
            name_list.append(product["name"])
            amount_list.append(product["amount"])
        else:
            name_list_a.append(product["name"])
            amount_list_a.append(product["amount"])



    res = dict(map(lambda i: (i,id_list.count(i-1)), id_list[:-1]))

    url = f"https://api.digiseller.ru/api/seller-sells/v2?token={t}"

    start = str(datetime.date.today()) + " 00:00:00"
    end = str(datetime.date.today()) + " 23:59:59"

    json = {
        "product_ids": id_list,
        "date_start": start,
        "date_finish": end,
        "returned": "1",
        "page": 1,
        "rows": 10
    }
    r = requests.post(url, json=json)

    for i in r.json()["rows"]:
        if i["product_id"] in id_list:
            for j in res:
                if j == i["product_id"]:
                    res[j] += 1
    #print(name_list)
    #print(amount_list)
    #print(res)
    #print(a)

    a = res.values()

    df = pd.DataFrame({'название': name_list,
                       'рекламная ставка': amount_list,
                       'продажи сегодня': a})

    df.to_excel('./own.xlsx')

    df = pd.DataFrame({'название': name_list_a,
                       'рекламная ставка': amount_list_a})

    df.to_excel('./other.xlsx')




def main():
    get_data()
