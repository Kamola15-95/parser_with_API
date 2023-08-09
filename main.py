import requests
import json
import psycopg2


def get_category():

    url = 'https://catalog.wb.ru/catalog/gift11/catalog?appType=1&cat=130603&curr=uzs&dest=491&regions=4,68,102,70,69,30,86,40,1,66,48,110,31,22,114&sort=popular&spp=0'

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://uz.wildberries.ru',
        'Referer': 'https://uz.wildberries.ru/catalog/podarki/detyam/igrushki',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'macOS'
        }

    response = requests.get(url=url, headers=headers)

    return response.json()

def prepare_items(response):

    products = []

    all_products = response.get('data', {}).get('products')

    if all_products != None and len(all_products) > 0:
        for product in all_products:
            products.append({
                'brand': product.get('brand'),
                'name': product.get('name'),
                'priceU': float(product.get('priceU')) / 100 if product.get('priceU') != None else None, # Так как в запросе почему-то еще 2 нуля добавлено
                'salePriceU': float(product.get('salePriceU')) / 100 if product.get('salePriceU') != None else None
            })

    return products

def main():
    response = get_category()
    products = prepare_items(response)

    with open('products.json', mode='w', encoding='UTF-8') as file:
        json.dump(products, file, ensure_ascii=False, indent=4)

def save_json_to_database(filename):
    with open(filename, mode='r', encoding='UTF-8') as file:
        data = json.load(file)

    db = sqlite3.connect('products.db')
    cursor = db.cursor()

    db.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            name TEXT,
            priceU REAL,
            salePriceU REAL
        )
    ''')
    for product in data:
        db.execute('''
            INSERT INTO products (brand, name, priceU, salePriceU)
            VALUES (?, ?, ?, ?)
        ''', (
            product['brand'],
            product['name'],
            product['priceU'],
            product['salePriceU']
        ))

    db.commit()
    db.close()

    print('Файл сохранен в базу данных')

save_json_to_database('products.json')


