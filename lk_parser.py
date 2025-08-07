import json
import os

import requests
from utils import SessionKeeper, process_grades, visualize_diff
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(dbname=os.getenv("DB_NAME"),
                        user="postgres",
                        password=os.getenv("DB_PASSWORD"),
                        host='localhost')
cursor = conn.cursor()

lk_start_url = 'https://lk.gubkin.ru/new/login'

login = os.getenv("LOGIN")

password = os.getenv("PASSWORD")


def authorize_and_get_cookie(login, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(lk_start_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(login)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input.base-submit.form-submit").click()
    all_cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict


if __name__ == '__main__':
    # driver.implicitly_wait(5)
    # keeper = SessionKeeper(driver)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Первоначальная авторизация и загрузка данных
    print("Открываем страницу входа...")
    driver.get(lk_start_url)

    print('Ждём пока появится поле ввода и вводим туда юз')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(login)

    print('Вводим пароль')
    driver.find_element(By.NAME, "password").send_keys(password)

    print('Нажимаем на кнопку')
    driver.find_element(By.CSS_SELECTOR, "input.base-submit.form-submit").click()

    all_cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
    api_url = f"https://lk.gubkin.ru/new//api/api.php?module=study&resource=Performance&method=getPerformance&studentId={login}-1"

    while True:
        time.sleep(3)
        response = process_grades(requests.get(api_url, cookies=cookies_dict).json())
        print(response)
        # save_grades_to_file(response) - красивое сохранение в файл
        cursor.execute('''
                SELECT data FROM grades 
                WHERE user_id = %s
                ORDER BY changed_at DESC LIMIT 1
            ''', (1,))
        last_value = cursor.fetchone()[0]
        if last_value != response:
            print('Изменения!')
            difference = visualize_diff(last_value, response)
            for diff in difference:
                if "replace" in diff or "add" in diff:
                    print(diff["value"])
            # print(difference)
            cursor.execute("""
                        UPDATE grades
                        SET data = %s, 
                            changed_at = %s
                        WHERE user_id = (
                            SELECT user_id 
                            FROM grades 
                            WHERE user_id = %s
                            ORDER BY changed_at DESC 
                            LIMIT 1
                        )
                    """, (json.dumps(response), datetime.now(), 1))

            conn.commit()
