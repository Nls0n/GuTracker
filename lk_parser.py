import json
import os
import time
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class LKParser:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user="postgres",
            password=os.getenv("DB_PASSWORD"),
            host='localhost'
        )
        self.cursor = self.conn.cursor()
        self.lk_url = 'https://lk.gubkin.ru/new/login'
        self._api_url = None
        self._cookies = None
        self._login = None
        self._password = None
        self._uid = None
        self.session = requests.Session()  # Создаем сессию здесь
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://lk.gubkin.ru/new/',
            'X-Requested-With': 'XMLHttpRequest'
        })

    @property
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies):
        self._cookies = cookies

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._api_url = f"https://lk.gubkin.ru/new//api/api.php?module=study&resource=Performance&method=getPerformance&studentId={self._login}-1"
        self._password = value

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    def get_cookies(self, login: str, password: str):
        """Авторизация в ЛК через Selenium"""
        self.login = login
        self.password = password
        chrome_options = Options()

        # Базовые настройки для ускорения
        chrome_options.add_argument("--headless")  # Режим без GUI
        chrome_options.add_argument("--disable-gpu")  # Отключение GPU
        chrome_options.add_argument("--no-sandbox")  # Обход sandbox безопасности
        chrome_options.add_argument("--disable-dev-shm-usage")  # Избегание проблем с /dev/shm

        # Оптимизации загрузки
        chrome_options.add_argument("--disable-extensions")  # Отключение расширений
        chrome_options.add_argument("--disable-infobars")  # Отключение информационных панелей
        chrome_options.add_argument("--disable-browser-side-navigation")  # Отключение навигации на стороне браузера
        chrome_options.add_argument("--disable-features=NetworkService")  # Отключение некоторых сетевых сервисов

        # Ускорение загрузки страниц
        chrome_options.page_load_strategy = 'eager'  # Загрузка только DOM

        # Отключение ненужных функций
        chrome_options.add_argument("--disable-notifications")  # Уведомления
        chrome_options.add_argument("--disable-popup-blocking")  # Блокировка попапов
        chrome_options.add_argument("--disable-default-apps")  # Стандартные приложения Chrome
        chrome_options.add_argument("--disable-translate")  # Переводчик Google

        # Оптимизации JavaScript
        chrome_options.add_argument("--disable-javascript")  # Полное отключение JS
        # ИЛИ более тонкие настройки:
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Отключение загрузки изображений

        # Сетевые оптимизации
        chrome_options.add_argument("--disable-web-security")  # Отключение политики CORS
        chrome_options.add_argument("--allow-running-insecure-content")  # Разрешение небезопасного контента

        # Экспериментальные настройки для ускорения
        chrome_options.add_argument(
            "--enable-features=NetworkServiceInProcess")  # Экспериментальная сетевая оптимизация
        chrome_options.add_argument("--disable-software-rasterizer")  # Отключение софтверного растеризатора

        # Настройки профиля
        chrome_options.add_argument("--user-data-dir=/tmp/chrome_profile")  # Использование временного профиля
        chrome_options.add_argument("--disable-sync")  # Отключение синхронизации Chrome

        # Инициализация драйвера с оптимизированными настройками
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        try:
            driver.get(self.lk_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            ).send_keys(login)
            driver.find_element(By.NAME, "password").send_keys(password)
            driver.find_element(By.CSS_SELECTOR, "input.base-submit.form-submit").click()
            all_cookies = driver.get_cookies()
            cookies = {
                c['name']: c['value']
                for c in all_cookies
                if c['domain'] == 'lk.gubkin.ru'
            }
            return cookies
        finally:
            driver.quit()

    async def check_grades_updates(self, user_id: int, login: str, password: str):
        """Проверка изменений в оценках"""
        self.uid = user_id
        self.login = login
        self.password = password
        is_registered, _ = await self.test_credentials(login, password)
        cookies = self.get_cookies(login, password)
        if not cookies or not is_registered:
            logger.error("Не удалось получить куки")
            return []
        self.session.cookies.clear()
        self.session.cookies.update(cookies)
        params = {
            'module': 'study',
            'resource': 'Performance',
            'method': 'getPerformance',
            'studentId': f"{login}-1",
            '_': int(time.time() * 1000)  # Добавляем timestamp для избежания кэширования
        }
        try:
            response = self.session.get(
                "https://lk.gubkin.ru/new/api/api.php",
                params=params,
                timeout=10
            )
            response.raise_for_status()  # Проверяем статус ответа
            data = response.json()
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")
            return []
        data = self.process_grades(data)
        self.cursor.execute('''
                SELECT data FROM grades 
                WHERE user_id = %s
                ORDER BY changed_at DESC LIMIT 1
            ''', (user_id,))

        last_grades = self.cursor.fetchone()[0] if self.cursor.rowcount else {}

        if last_grades != data:
            differences = self._find_json_differences(last_grades, data)
            self._save_to_db(user_id, data)
            return differences
        return []

    def process_grades(self, json_data: dict):
        """Обработка сырых данных из ЛК"""
        beauty_data = []
        if json_data["success"] is True:
            for subject in json_data["result"]["performance"]:
                current_subject = dict()
                current_subject[f"{subject["name"]}"] = f"{subject["currentPoints"]} баллов из {subject["maxPoints"]}"
                for work in subject["works"]:
                    if works := current_subject.get("Работы", None) is not None:
                        current_subject[
                            "Работы"].append(
                            f"{work["currentPoints"]} баллов из {work["maxPoints"]} за {work["testName"]} - {work["name"]} Дедлайн - {work["weekNumber"]} неделя.")
                    else:
                        current_subject["Работы"] = [
                            f"{work["currentPoints"]} баллов из {work["maxPoints"]} за {work["testName"]} - {work["name"]} Дедлайн - {work["weekNumber"]} неделя."]
                beauty_data.append(current_subject)
        return beauty_data

    def _find_json_differences(self, old_data, new_data, path="", differences=None):
        """
        Рекурсивно находит различия между двумя JSON-совместимыми структурами данных.

        Args:
            old_data: Исходные данные (dict/list)
            new_data: Новые данные (dict/list)
            path: Текущий путь в структуре (для рекурсии)
            differences: Список для накопления различий (для рекурсии)

        Returns:
            list: Список строк с описанием различий
        """
        if differences is None:
            differences = []

        # Типы данных не совпадают
        if type(old_data) != type(new_data):
            differences.append(f"{path}: Тип изменился с {type(old_data)} на {type(new_data)}")
            return differences

        # Сравнение словарей
        if isinstance(old_data, dict):
            # Проверка удаленных ключей
            for key in old_data.keys() - new_data.keys():
                differences.append(f"{path}.{key}: Ключ удален (значение было: {old_data[key]!r})")

            # Проверка добавленных ключей
            for key in new_data.keys() - old_data.keys():
                differences.append(f"Ключ добавлен (новое значение: {new_data[key]!r})")

            # Проверка измененных значений для общих ключей
            for key in old_data.keys() & new_data.keys():
                self._find_json_differences(
                    old_data[key],
                    new_data[key],
                    f"{path}.{key}" if path else key,
                    differences
                )

        # Сравнение списков
        elif isinstance(old_data, list):
            if len(old_data) != len(new_data):
                differences.append(f"{path}: Длина списка изменилась с {len(old_data)} на {len(new_data)}")

            for i, (old_item, new_item) in enumerate(zip(old_data, new_data)):
                self._find_json_differences(
                    old_item,
                    new_item,
                    f"{path}[{i}]",
                    differences
                )

        # Сравнение простых значений
        else:
            if old_data != new_data:
                differences.append(f"Значение изменилось с {old_data!r} на {new_data!r}")

        return differences

    def _save_to_db(self, user_id: int, data: list):
        """Сохранение в БД"""
        self.uid = user_id
        self.cursor.execute("""
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
                            """, (json.dumps(data), datetime.now(), user_id))

        self.conn.commit()

    async def test_credentials(self, login: str, password: str):
        """Проверка валидности логина/пароля"""
        self.login = login
        self.password = password
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        try:
            driver.get(self.lk_url)
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
            all_cookies = driver.get_cookies()
            cookies_dict = {}
            for cookie in all_cookies:
                cookies_dict[cookie['name']] = cookie['value']

            if driver.current_url == 'https://lk.gubkin.ru/new/#/info/news':
                return True, cookies_dict
            else:
                return False
        except Exception as e:
            return f"Произошла ошибка {e}"

    async def get_current_grades(self, login: int, password: str):
        """Получение текущих оценок"""
        self.login = login
        self.password = password
        cookies = self.get_cookies(login, password)
        if not cookies:
            logger.error("Не удалось получить куки")
            return []
        self.session.cookies.clear()
        self.session.cookies.update(cookies)
        params = {
            'module': 'study',
            'resource': 'Performance',
            'method': 'getPerformance',
            'studentId': f"{login}-1",
            '_': int(time.time() * 1000)  # Добавляем timestamp для избежания кэширования
        }
        try:
            response = self.session.get(
                "https://lk.gubkin.ru/new/api/api.php",
                params=params,
                timeout=10
            )
            response.raise_for_status()  # Проверяем статус ответа
            data = response.json()
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")
            return []
        data = self.process_grades(data)
        return data


instance = LKParser()
# print(instance.check_grades_updates(1, instance.login, instance.password))
# print(instance.test_credentials(login=instance.login, password=instance.password))
# print(instance.get_cookies(login=instance.login, password=instance.password))
print('---')
print(instance.get_current_grades(instance.login, instance.password))
