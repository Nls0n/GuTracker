import os
import time

import requests
import psycopg2
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

url = 'https://lk.gubkin.ru/new//api/api.php?module=study&resource=Performance&method=getPerformance&studentId=152558-1'

data = requests.get(url, headers={
    "Cookie": "PHPSESSID=d5ackj19rif2vj5c167lv0lc41;"})

print(data.text)
conn = psycopg2.connect(dbname='GuTracker',
                        user="postgres",
                        password='A12138877',
                        host='localhost')
cursor = conn.cursor()


def keep_only_last_record(user_id):
    conn = None
    try:
        conn = psycopg2.connect(
            dbname='GuTracker',
            user="postgres",
            password='A12138877',
            host='localhost'
        )
        cursor = conn.cursor()

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
                """, (json.dumps([12, 3, 4, 5]), datetime.now(), 1))

        conn.commit()


    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при удалении записей: {error}")
        return 0
    finally:
        if conn is not None:
            conn.close()


# Пример использования
user_id = 1  # ID пользователя
deleted_count = keep_only_last_record(user_id)
print(f"Удалено записей: {deleted_count}")
def check_credentials(login,password):
    lk_url = 'https://lk.gubkin.ru/new/login'
    login = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(lk_url)
    # print('зашли на урл лк')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    ).send_keys(login)
    # print('ввели логин')
    driver.find_element(By.NAME, "password").send_keys(password)
    # print('ввели пароль')
    driver.find_element(By.CSS_SELECTOR, "input.base-submit.form-submit").click()
    # print('нажали на кнопку')
    time.sleep(1)
    if driver.current_url == 'https://lk.gubkin.ru/new/#/info/news':
        return True
    else:
        return False

import json_tools


def visualize_diff(json1, json2):
    diff = json_tools.diff(json1, json2)
    if not diff:
        return "Различий нет"
    return diff


# Пример использования
json1 = {"a": 1, "b": {"c": 2}}
json2 = {"a": 1, "b": {"c": 3}}
print(visualize_diff(json1, json2))
