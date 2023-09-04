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
with open('naver_products.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

try:
    with connection.cursor() as cursor:
        for item in data:
            formatted_date = datetime.strptime(item['register_date'], "%Y.%m").strftime("%Y-%m-%d 00:00:00")

            # 데이터 삽입
            sql_insert = "INSERT INTO products (category, title, cost, images, amount, register_date, sale) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_insert, (
                item['category'],
                item['title'],
                item['price'],
                item['image'],
                int(item['amount']),
                formatted_date,
                int(item['sale'])
            ))

        connection.commit()
finally:
    connection.close()

# JSON 파일명에 날짜 저장 (원본 파일 덮어쓰기)
current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_filename = f'naver_products_{current_date}.json'

with open(output_filename, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)