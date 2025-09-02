import random
import time
from datetime import datetime

class SessionKeeper:
    def __init__(self, driver):
        self.driver = driver
        self.last_activity = time.time()

    def scroll(self):
        scroll_amount = random.randint(200, 400)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(0.5)
        self.driver.execute_script(f"window.scrollBy(0, {-scroll_amount // 2});")
        self.last_activity = time.time()


def process_grades(json_data):
    beauty_data = []
    if json_data["success"] is True:
        for subject in json_data["result"]["performance"]:
            current_subject = dict()
            current_subject[f"{subject["name"]}"] = f"{subject["currentPoints"]} баллов из {subject["maxPoints"]}"
            for work in subject["works"]:
                if works := current_subject.get("Работы", None) is not None:
                    current_subject[
                        "Работы"].append(f"{work["currentPoints"]} баллов из {work["maxPoints"]} за {work["testName"]} - {work["name"]}\n Дедлайн - {work["weekNumber"]} неделя.")
                else:
                    current_subject["Работы"] = [f"{work["currentPoints"]} баллов из {work["maxPoints"]} за {work["testName"]} - {work["name"]}\n Дедлайн - {work["weekNumber"]} неделя."]
            beauty_data.append(current_subject)
    return beauty_data


def save_grades_to_file(data, filename="grades_report.txt"):
    with open(filename, 'w', encoding='utf-8') as file:
        for subject in data:
            # Записываем название предмета и общий балл
            subject_name = list(subject.keys())[0]
            file.write(f"════════════════════════════════════════\n")
            file.write(f"📚 {subject_name}\n")
            file.write(f"🔹 {subject[subject_name]}\n\n")

            # Записываем работы по предмету
            if 'Работы' in subject and subject['Работы']:
                file.write("📝 Работы:\n")
                for i, work in enumerate(subject['Работы'], 1):
                    # Форматируем строку работы
                    work = work.replace('\n', ' ')  # Убираем переносы строк
                    work = work.replace('  ', ' ')  # Убираем двойные пробелы

                    # Разделяем баллы и описание
                    if 'за' in work:
                        parts = work.split('за', 1)
                        points_part = parts[0].strip()
                        desc_part = 'за ' + parts[1].strip()
                        file.write(f"   {i}. {points_part}\n     {desc_part}\n")
                    else:
                        file.write(f"   {i}. {work}\n")
                file.write("\n")
            else:
                file.write("ℹ️ Нет данных о работах\n\n")

        file.write("════════════════════════════════════════\n")
        file.write(f"📅 Отчёт сформирован: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")

    print(f"✅ Отчёт успешно сохранён в файл {filename}")


def clean_json(data):
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = clean_json(value)
        return result

    elif isinstance(data, list):
        return [clean_json(item) for item in data]

    elif data is None or data == "":
        return 0

    else:
        return data