import pymysql
import os
import json
from datetime import datetime

# 환경 변수에서 데이터베이스 연결 정보 가져오기
db_host = os.environ.get('DB_HOST') # localhost
db_user = os.environ.get('DB_USER') # root
db_password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME') # emp

# MySQL 연결 설정
connection = pymysql.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    db=db_name,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# JSON 파일 불러오기
with open('coupang_products.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

try:
    with connection.cursor() as cursor:
        for item in data:
            price = int(item['price'].replace(',', ''))
            sql_select = "SELECT COUNT(*) FROM products WHERE title = %s"
            cursor.execute(sql_select, (item['title'],))
            existing_data_count = cursor.fetchone()[0]

            if existing_data_count > 0:
                sql_update = "UPDATE products SET category = %s, cost = %s, images = %s, amount = %s, register_date = %s, sale = %s WHERE title = %s"
                cursor.execute(sql_update, (
                    item['category'],
                    price,
                    item['image'],
                    int(item['amount']),
                    datetime.strptime(item['register_date'], "%Y-%m-%d %H:%M:%S"),
                    bool(item['sale']),
                    item['title']
                ))
            else:
                sql_insert = "INSERT INTO products (category, title, cost, images, amount, register_date, sale) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_insert, (
                    item['category'],
                    item['title'],
                    price,
                    item['image'],
                    int(item['amount']),
                    datetime.strptime(item['register_date'], "%Y-%m-%d %H:%M:%S"),
                    bool(item['sale'])
                ))

        connection.commit()


finally:
    connection.close()