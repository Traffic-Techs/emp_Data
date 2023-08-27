import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import time
import random
from datetime import datetime
import json

# 쿠팡의 robots.txt 확인
url = "https://coupang.com"
robot_url = urljoin(url, "/robots.txt")

robot_parser = RobotFileParser()
robot_parser.set_url(robot_url)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Accept-Language": "ko - KR, ko; q = 0.9, en - US; q = 0.8, en;q = 0.7"}

r = requests.get(robot_url, headers=headers)

if r.status_code == 200:
    robot_parser.parse(r.text.splitlines())

if robot_parser.can_fetch("Naverbot", url):
    print("Allow")

    user_categories = [178399, 395267, 429603, 497135, 497136, 497141, 497142, 497159, 497198, 497220, 497244, 497245]

    results = []

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-blink-features-AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                           {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})

    for user_category in user_categories:
        print(f"Crawling products for category: {user_category}")

        start_page = 1

        while True: # 무한 루프로 페이지 순회
            url = f"https://www.coupang.com/np/categories/{user_category}?page={start_page}"
            driver.get(url)
            time.sleep(5)

            category_element = driver.find_element(By.CLASS_NAME, "newcx-product-list-title")
            category = category_element.text.strip()

            try:
                ul = driver.find_element(By.ID, 'productList')
                lis = ul.find_elements(By.TAG_NAME, 'li')
                if not lis:
                    print("No more products on this page.")
                    break
                for li in lis:
                    try:
                        title = li.find_element(By.CLASS_NAME, 'name').text
                        price = li.find_element(By.CLASS_NAME, 'price-value').text
                        image = li.find_element(By.TAG_NAME, 'img').get_attribute("src")

                        sale_element = None
                        try:
                            sale_element = li.find_element(By.CLASS_NAME, 'out-of-stock')
                            sale = "false"
                        except:
                            sale = "true"

                        product_data = {
                            "category": category,
                            "title": title,
                            "price": price,
                            "image": image,
                            "amount": random.randint(1, 10000),
                            "register_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "sale": sale
                        }
                        results.append(product_data)

                    except Exception:
                        pass
            except Exception:
                print("Product list not found on the page.")
                break  # 해당 카테고리의 크롤링을 중지하고 다음 카테고리로 이동

            start_page += 1
        print(f"Crawling for category {user_category} finished.")

    driver.quit()

    # JSON 파일로 저장
    with open("coupang_products.json", "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)
else:
    print("Disallow")