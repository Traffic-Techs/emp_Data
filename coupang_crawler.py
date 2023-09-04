import json
import random
import re
import time
import requests
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless=new")
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})

url = 'https://www.coupang.com/'
driver.get(url)
driver.implicitly_wait(10)

driver.find_element(By.XPATH, '//*[@id="header"]/div').click()
driver.find_element(By.XPATH, '//*[@id="gnbAnalytics"]/ul[1]/li[8]/a').click()
print("디지털 카테고리 접속")
time.sleep(1)

results = []

def sub_crawling(new_category_number):
    start_page = 1

    while True:
        new_url = f"https://www.coupang.com/np/categories/{new_category_number}?page={start_page}"
        driver.get(new_url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept-Language": "ko - KR, ko; q = 0.9, en - US; q = 0.8, en;q = 0.7"}

        response = requests.get(new_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            category_element = soup.find(class_='newcx-product-list-title')
            category = category_element.text.strip()

            ul = soup.find(id='productList')
            lis = ul.find_all('li')

            if not lis:
                break

            for li in lis:
                try:
                    link = li.find('a')['href']
                    title = li.find(class_='name').text
                    price = li.find(class_='price-value').text
                    image = li.find('img')['src']

                    sale_element = li.find(class_='out-of-stock')
                    sale = "false" if sale_element else "true"

                    product_data = {
                        "category": category,
                        "title": title,
                        "price": price,
                        "image": image,
                        "link": "coupang.com" + link,
                        "amount": random.randint(1, 10000),
                        "register_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "sale": sale
                    }
                    results.append(product_data)
                except Exception as e:
                    pass
        except Exception:
            print("Product list not found on the page.")
            break  # 해당 카테고리의 크롤링을 중지하고 다음 카테고리로 이동

        start_page += 1
    print(f"Crawling finished.")




select_category_start = 10
select_category_end = 27

for category_number in range(select_category_start, select_category_end + 1):

    xpath_expression = f'//*[@id="searchCategoryComponent"]/ul/li[{category_number}]/label'
    target_category = driver.find_element(By.XPATH, xpath_expression)
    target_category.click()
    time.sleep(15)

    current_url = driver.current_url
    print(current_url)

    match = re.search(r'categories/(\d+)', current_url)

    if match:
        new_category_number = match.group(1)
        print("추출된 카테고리 번호:", new_category_number)
        sub_crawling(new_category_number)

        start_li = 1
        sub_category_number = int(new_category_number) - 100
        while True:
            xpath_expression = f'//*[@id="category{sub_category_number}"]/li[{start_li}]/label'

            if xpath_expression:
                try:
                    sub_category = driver.find_element(By.XPATH, xpath_expression)
                    sub_category.click()
                    time.sleep(15)
                    final_url = driver.current_url

                    match = re.search(r'categories/(\d+)', final_url)

                    if match:
                        new_category_number = match.group(1)
                        print("실제 카테고리 번호:", new_category_number)

                    sub_crawling(new_category_number)

                except NoSuchElementException:
                    break

                start_li += 1
                sub_category_number = sub_category_number

            else:
                break

    else:
        pass

# 드라이버 종료
driver.quit()
current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# JSON 파일로 저장
with open(f"coupang_products.json_{current_date}", "w", encoding="utf-8") as json_file:
    json.dump(results, json_file, ensure_ascii=False, indent=4)
