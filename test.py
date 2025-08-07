import requests
import psycopg2
import json
from datetime import datetime
url = 'https://lk.gubkin.ru/new//api/api.php?module=study&resource=Performance&method=getPerformance&studentId=152558-1'

data = requests.get(url, headers={
    "Cookie": "_ym_uid=1742472013112489877; _ym_d=1742472013; PHPSESSID=2s0ukgms4vssb4q81psd32u341; tmr_lvid=b2deb66cc34bd5e375af2971f925fe96; tmr_lvidTS=1748711464098; MoodleSession=2e8271r0fk52np65co51rrf6qf; MOODLEID1_=%25AAEw9%2595%2518"})

print(data.text)
conn = psycopg2.connect(dbname='GuTracker',
                        user="postgres",
                        password='A12138877',
                        host='localhost')
cursor = conn.cursor()

import psycopg2


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
                """, (json.dumps([12,3,4,5]), datetime.now(), 1))

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


data = {'success': True, 'result': {'performance': [
    {'name': 'Деловой этикет и культура коммуникации.', 'courseWork': None, 'currentPoints': '53', 'maxPoints': '100',
     'studyItems': [], 'stages': {'passed': {'quantity': 3, 'currentPoints': 53, 'maxPoints': 100},
                                  'debt': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                                  'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': 'Пишем деловые документы', 'testName': 'Домашнее задание. №1', 'weekNumber': '6',
         'currentPoints': '20', 'maxPoints': '25', 'vblid': '874109', 'contid': '8', 'nomer': '1',
         'fileAttached': False},
        {'name': 'визитки', 'testName': 'Домашнее задание. №2', 'weekNumber': '16', 'currentPoints': '23',
         'maxPoints': '25', 'vblid': '874109', 'contid': '8', 'nomer': '2', 'fileAttached': False},
        {'name': 'ответы студентов', 'testName': 'Активная работа на семинаре. №1', 'weekNumber': '17',
         'currentPoints': '10', 'maxPoints': '50', 'vblid': '874109', 'contid': '11', 'nomer': '1',
         'fileAttached': False}]},
    {'name': 'Иностранный язык (английский) 2.', 'courseWork': None, 'currentPoints': '86', 'maxPoints': '100',
     'studyItems': [], 'stages': {'passed': {'quantity': 3, 'currentPoints': 86, 'maxPoints': 100},
                                  'debt': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                                  'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': '', 'testName': 'Контрольная работа. №1', 'weekNumber': '7', 'currentPoints': '25', 'maxPoints': '30',
         'vblid': '874112', 'contid': '1', 'nomer': '1', 'fileAttached': False},
        {'name': '', 'testName': 'Итоговая контрольная работа. №1', 'weekNumber': '16', 'currentPoints': '36',
         'maxPoints': '40', 'vblid': '874112', 'contid': '5', 'nomer': '1', 'fileAttached': False},
        {'name': '', 'testName': 'Контрольная работа. №1', 'weekNumber': '14', 'currentPoints': '25', 'maxPoints': '30',
         'vblid': '874112', 'contid': '16', 'nomer': '1', 'fileAttached': False}]},
    {'name': 'Интегралы, ряды, функции многих переменных.', 'courseWork': None, 'currentPoints': '30',
     'maxPoints': '60', 'studyItems': [], 'stages': {'passed': {'quantity': 5, 'currentPoints': 30, 'maxPoints': 60},
                                                     'debt': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                                                     'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}},
     'works': [{'name': 'Неопределённые интегралы', 'testName': 'Контрольная работа. №1', 'weekNumber': '5',
                'currentPoints': '6', 'maxPoints': '15', 'vblid': '874104', 'contid': '1', 'nomer': '1',
                'fileAttached': False},
               {'name': 'Приложения определённых интегралов', 'testName': 'Контрольная работа. №2', 'weekNumber': '8',
                'currentPoints': '5', 'maxPoints': '10', 'vblid': '874104', 'contid': '1', 'nomer': '2',
                'fileAttached': False},
               {'name': 'Ряды', 'testName': 'Контрольная работа. №1', 'weekNumber': '11', 'currentPoints': '8',
                'maxPoints': '12', 'vblid': '874104', 'contid': '16', 'nomer': '1', 'fileAttached': False},
               {'name': 'ФМП', 'testName': 'Контрольная работа. №2', 'weekNumber': '13', 'currentPoints': '6',
                'maxPoints': '8', 'vblid': '874104', 'contid': '16', 'nomer': '2', 'fileAttached': False},
               {'name': 'Дифференциальные уравнения', 'testName': 'Контрольная работа. №3', 'weekNumber': '16',
                'currentPoints': '5', 'maxPoints': '15', 'vblid': '874104', 'contid': '16', 'nomer': '3',
                'fileAttached': False}]},
    {'name': 'Основы алгоритмизации и программирования.', 'courseWork': None, 'currentPoints': '51.8',
     'maxPoints': '60', 'studyItems': [], 'stages': {'passed': {'quantity': 12, 'currentPoints': 51.8, 'maxPoints': 60},
                                                     'debt': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                                                     'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}},
     'works': [
         {'name': '', 'testName': 'Контрольная работа. №1', 'weekNumber': '4', 'currentPoints': '4.8', 'maxPoints': '5',
          'vblid': '874106', 'contid': '1', 'nomer': '1', 'fileAttached': False},
         {'name': '', 'testName': 'Контрольная работа. №2', 'weekNumber': '11', 'currentPoints': '2', 'maxPoints': '7',
          'vblid': '874106', 'contid': '1', 'nomer': '2', 'fileAttached': False},
         {'name': '', 'testName': 'Домашнее задание. №1', 'weekNumber': '15', 'currentPoints': '4', 'maxPoints': '4',
          'vblid': '874106', 'contid': '8', 'nomer': '1', 'fileAttached': False},
         {'name': '', 'testName': 'Домашнее задание. №2', 'weekNumber': '15', 'currentPoints': '4', 'maxPoints': '4',
          'vblid': '874106', 'contid': '8', 'nomer': '2', 'fileAttached': False},
         {'name': '', 'testName': 'Активная работа на семинаре. №1', 'weekNumber': '4', 'currentPoints': '2',
          'maxPoints': '2', 'vblid': '874106', 'contid': '11', 'nomer': '1', 'fileAttached': False},
         {'name': '', 'testName': 'Активная работа на семинаре. №2', 'weekNumber': '8', 'currentPoints': '2',
          'maxPoints': '2', 'vblid': '874106', 'contid': '11', 'nomer': '2', 'fileAttached': False},
         {'name': '', 'testName': 'Активная работа на семинаре. №3', 'weekNumber': '10', 'currentPoints': '3',
          'maxPoints': '3', 'vblid': '874106', 'contid': '11', 'nomer': '3', 'fileAttached': False},
         {'name': '', 'testName': 'Активная работа на семинаре. №4', 'weekNumber': '12', 'currentPoints': '2',
          'maxPoints': '2', 'vblid': '874106', 'contid': '11', 'nomer': '4', 'fileAttached': False},
         {'name': '', 'testName': 'Активная работа на семинаре. №5', 'weekNumber': '16', 'currentPoints': '3',
          'maxPoints': '3', 'vblid': '874106', 'contid': '11', 'nomer': '5', 'fileAttached': False},
         {'name': '', 'testName': 'Активная работа на семинаре. №6', 'weekNumber': '17', 'currentPoints': '5',
          'maxPoints': '5', 'vblid': '874106', 'contid': '11', 'nomer': '6', 'fileAttached': False},
         {'name': '', 'testName': 'Контрольная работа. №1', 'weekNumber': '15', 'currentPoints': '8', 'maxPoints': '10',
          'vblid': '874106', 'contid': '16', 'nomer': '1', 'fileAttached': False},
         {'name': '', 'testName': 'Контрольная работа. №2', 'weekNumber': '17', 'currentPoints': '12',
          'maxPoints': '13', 'vblid': '874106', 'contid': '16', 'nomer': '2', 'fileAttached': False}]},
    {'name': 'Основы алгоритмизации и программирования: курсовая работа.', 'courseWork': {
        'theme': 'Разработка и исследование методов и алгоритмов решения вычислительных и комбинаторных задач.',
        'teacherName': 'Костандян В.А. ', 'teacherDivision': 'кафедра информатики', 'teacherJobTitle': 'Доцент'},
     'currentPoints': '', 'maxPoints': '0', 'studyItems': [],
     'stages': {'passed': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                'debt': {'quantity': 1, 'currentPoints': None, 'maxPoints': 0},
                'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': '', 'testName': 'Не введен учебный план. №', 'weekNumber': '', 'currentPoints': None, 'maxPoints': '',
         'vblid': '874107', 'contid': '', 'nomer': '', 'fileAttached': False}]},
    {'name': 'Основы механики и молекулярная физика.', 'courseWork': None, 'currentPoints': '29.5', 'maxPoints': '60',
     'studyItems': [], 'stages': {'passed': {'quantity': 10, 'currentPoints': 29.5, 'maxPoints': 45},
                                  'debt': {'quantity': 1, 'currentPoints': 0, 'maxPoints': 15},
                                  'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': '«Ознакомление с теорией погрешностей»', 'testName': 'Лабораторная работа. №1', 'weekNumber': '4',
         'currentPoints': '3.5', 'maxPoints': '4', 'vblid': '874105', 'contid': '2', 'nomer': '1',
         'fileAttached': False}, {
            'name': '«Изучение законов равномерного и равноускоренного движения» «Применение закона сохранения импульса при изучении центрального удара шаров»',
            'testName': 'Лабораторная работа. №2', 'weekNumber': '6', 'currentPoints': '3', 'maxPoints': '4',
            'vblid': '874105', 'contid': '2', 'nomer': '2', 'fileAttached': False},
        {'name': 'Определение момента инерции маятника Обербека.Определение момента инерции маятника Максвелла ',
         'testName': 'Лабораторная работа. №3', 'weekNumber': '10', 'currentPoints': '2.5', 'maxPoints': '4',
         'vblid': '874105', 'contid': '2', 'nomer': '3', 'fileAttached': False}, {
            'name': 'Определение коэффициента поверхностного натяжения воды на границе с воздухом методом отрыва кольца. Определение динамической вязкости жидкости  по методу Стокса. ',
            'testName': 'Лабораторная работа. №4', 'weekNumber': '13', 'currentPoints': '4', 'maxPoints': '4',
            'vblid': '874105', 'contid': '2', 'nomer': '4', 'fileAttached': False},
        {'name': 'Определение соотношения теплоемкостей   по методу Клемана-Дезорма. ',
         'testName': 'Лабораторная работа. №5', 'weekNumber': '15', 'currentPoints': '3', 'maxPoints': '4',
         'vblid': '874105', 'contid': '2', 'nomer': '5', 'fileAttached': False},
        {'name': 'Кинематика и динамика материальной точки', 'testName': 'Тест. №1', 'weekNumber': '8',
         'currentPoints': '3', 'maxPoints': '3', 'vblid': '874105', 'contid': '10', 'nomer': '1',
         'fileAttached': False},
        {'name': 'Динамика вращательного движения. СТО.', 'testName': 'Тест. №2', 'weekNumber': '10',
         'currentPoints': '1.5', 'maxPoints': '2', 'vblid': '874105', 'contid': '10', 'nomer': '2',
         'fileAttached': False},
        {'name': 'Молекулярная физика', 'testName': 'Тест. №3', 'weekNumber': '14', 'currentPoints': '3',
         'maxPoints': '3', 'vblid': '874105', 'contid': '10', 'nomer': '3', 'fileAttached': False},
        {'name': 'Термодинамика', 'testName': 'Тест. №4', 'weekNumber': '15', 'currentPoints': '2', 'maxPoints': '2',
         'vblid': '874105', 'contid': '10', 'nomer': '4', 'fileAttached': False},
        {'name': 'Основы механики.', 'testName': 'Контрольная работа. №1', 'weekNumber': '8', 'currentPoints': '0',
         'maxPoints': '15', 'vblid': '874105', 'contid': '16', 'nomer': '1', 'fileAttached': False},
        {'name': 'Молекулярная физика. Термодинамика.', 'testName': 'Контрольная работа. №2', 'weekNumber': '16',
         'currentPoints': '4', 'maxPoints': '15', 'vblid': '874105', 'contid': '16', 'nomer': '2',
         'fileAttached': False}]},
    {'name': 'Периферийные устройства.', 'courseWork': None, 'currentPoints': '82.5', 'maxPoints': '100',
     'studyItems': [], 'stages': {'passed': {'quantity': 9, 'currentPoints': 82.5, 'maxPoints': 100},
                                  'debt': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                                  'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': 'Итоговая контрольная работа', 'testName': 'Итоговая контрольная работа. №1', 'weekNumber': '17',
         'currentPoints': '14', 'maxPoints': '20', 'vblid': '874110', 'contid': '5', 'nomer': '1',
         'fileAttached': False},
        {'name': 'Конфигурирование ПК', 'testName': 'Домашнее задание. №1', 'weekNumber': '7', 'currentPoints': '6',
         'maxPoints': '9', 'vblid': '874110', 'contid': '8', 'nomer': '1', 'fileAttached': False},
        {'name': 'Накопители информации', 'testName': 'Домашнее задание. №2', 'weekNumber': '10', 'currentPoints': '8',
         'maxPoints': '9', 'vblid': '874110', 'contid': '8', 'nomer': '2', 'fileAttached': False},
        {'name': 'Аудиосистема', 'testName': 'Домашнее задание. №3', 'weekNumber': '13', 'currentPoints': '8',
         'maxPoints': '9', 'vblid': '874110', 'contid': '8', 'nomer': '3', 'fileAttached': False},
        {'name': 'Видеосистема', 'testName': 'Домашнее задание. №4', 'weekNumber': '15', 'currentPoints': '7',
         'maxPoints': '9', 'vblid': '874110', 'contid': '8', 'nomer': '4', 'fileAttached': False},
        {'name': 'ЦАП и АЦП', 'testName': 'Контрольный опрос. №1', 'weekNumber': '5', 'currentPoints': '7.5',
         'maxPoints': '10', 'vblid': '874110', 'contid': '15', 'nomer': '1', 'fileAttached': False},
        {'name': 'Конфигурирование ПК и накопители информации', 'testName': 'Контрольный опрос. №2', 'weekNumber': '9',
         'currentPoints': '9', 'maxPoints': '10', 'vblid': '874110', 'contid': '15', 'nomer': '2',
         'fileAttached': False},
        {'name': 'Аудио и видео системы', 'testName': 'Контрольный опрос. №3', 'weekNumber': '15',
         'currentPoints': '10', 'maxPoints': '10', 'vblid': '874110', 'contid': '15', 'nomer': '3',
         'fileAttached': False},
        {'name': 'ЦАП и АЦП', 'testName': 'Домашнее задание. №1', 'weekNumber': '3', 'currentPoints': '13',
         'maxPoints': '14', 'vblid': '874110', 'contid': '17', 'nomer': '1', 'fileAttached': False}]},
    {'name': 'Правоведение.', 'courseWork': None, 'currentPoints': '70', 'maxPoints': '100', 'studyItems': [],
     'stages': {'passed': {'quantity': 11, 'currentPoints': 70, 'maxPoints': 95},
                'debt': {'quantity': 1, 'currentPoints': None, 'maxPoints': 5},
                'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': '', 'testName': 'Тест. №1', 'weekNumber': '17', 'currentPoints': '8', 'maxPoints': '10',
         'vblid': '874103', 'contid': '10', 'nomer': '1', 'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №1', 'weekNumber': '2', 'currentPoints': '3',
         'maxPoints': '5', 'vblid': '874103', 'contid': '11', 'nomer': '1', 'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №2', 'weekNumber': '4',
         'currentPoints': '10', 'maxPoints': '10', 'vblid': '874103', 'contid': '11', 'nomer': '2',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №3', 'weekNumber': '6',
         'currentPoints': '10', 'maxPoints': '10', 'vblid': '874103', 'contid': '11', 'nomer': '3',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №4', 'weekNumber': '8',
         'currentPoints': '10', 'maxPoints': '10', 'vblid': '874103', 'contid': '11', 'nomer': '4',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №5', 'weekNumber': '10',
         'currentPoints': '3', 'maxPoints': '10', 'vblid': '874103', 'contid': '11', 'nomer': '5',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №6', 'weekNumber': '12',
         'currentPoints': '6', 'maxPoints': '10', 'vblid': '874103', 'contid': '11', 'nomer': '6',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №7', 'weekNumber': '14',
         'currentPoints': '10', 'maxPoints': '10', 'vblid': '874103', 'contid': '11', 'nomer': '7',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №8', 'weekNumber': '15',
         'currentPoints': '2', 'maxPoints': '5', 'vblid': '874103', 'contid': '11', 'nomer': '8',
         'fileAttached': False},
        {'name': 'устный опрос', 'testName': 'Активная работа на семинаре. №9', 'weekNumber': '16',
         'currentPoints': None, 'maxPoints': '5', 'vblid': '874103', 'contid': '11', 'nomer': '9',
         'fileAttached': False},
        {'name': '', 'testName': 'Контрольная работа. №1', 'weekNumber': '14', 'currentPoints': '4', 'maxPoints': '5',
         'vblid': '874103', 'contid': '16', 'nomer': '1', 'fileAttached': False},
        {'name': '', 'testName': 'Домашнее задание. №1', 'weekNumber': '12', 'currentPoints': '4', 'maxPoints': '10',
         'vblid': '874103', 'contid': '17', 'nomer': '1', 'fileAttached': False}]},
    {'name': 'Профессионально-личностное саморазвитие.', 'courseWork': None, 'currentPoints': '72', 'maxPoints': '100',
     'studyItems': [], 'stages': {'passed': {'quantity': 4, 'currentPoints': 72, 'maxPoints': 100},
                                  'debt': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0},
                                  'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': 'КР 1', 'testName': 'Контрольная работа. №1', 'weekNumber': '12', 'currentPoints': '12',
         'maxPoints': '20', 'vblid': '874111', 'contid': '1', 'nomer': '1', 'fileAttached': False},
        {'name': 'КР 2', 'testName': 'Контрольная работа. №2', 'weekNumber': '16', 'currentPoints': '20',
         'maxPoints': '30', 'vblid': '874111', 'contid': '1', 'nomer': '2', 'fileAttached': False},
        {'name': 'ДЗ 2', 'testName': 'Домашнее задание. №1', 'weekNumber': '17', 'currentPoints': '10',
         'maxPoints': '20', 'vblid': '874111', 'contid': '8', 'nomer': '1', 'fileAttached': False},
        {'name': 'ДЗ 1', 'testName': 'Домашнее задание. №1', 'weekNumber': '14', 'currentPoints': '30',
         'maxPoints': '30', 'vblid': '874111', 'contid': '17', 'nomer': '1', 'fileAttached': False}]},
    {'name': 'Физическая культура 2.', 'courseWork': None, 'currentPoints': '32.1', 'maxPoints': '100',
     'studyItems': [], 'stages': {'passed': {'quantity': 4, 'currentPoints': 32.1, 'maxPoints': 90},
                                  'debt': {'quantity': 1, 'currentPoints': 0, 'maxPoints': 10},
                                  'forward': {'quantity': 0, 'currentPoints': None, 'maxPoints': 0}}, 'works': [
        {'name': 'Тест 1', 'testName': 'Тест. №1', 'weekNumber': '5', 'currentPoints': '9.1', 'maxPoints': '10',
         'vblid': '874113', 'contid': '10', 'nomer': '1', 'fileAttached': False},
        {'name': 'Тест 2', 'testName': 'Тест. №2', 'weekNumber': '7', 'currentPoints': '10', 'maxPoints': '10',
         'vblid': '874113', 'contid': '10', 'nomer': '2', 'fileAttached': False},
        {'name': 'АРС', 'testName': 'Активная работа на семинаре. №1', 'weekNumber': '17', 'currentPoints': '10',
         'maxPoints': '40', 'vblid': '874113', 'contid': '11', 'nomer': '1', 'fileAttached': False},
        {'name': 'КНФП 1', 'testName': 'Контрольные нормативы физической подготовленности. №1', 'weekNumber': '11',
         'currentPoints': '3', 'maxPoints': '30', 'vblid': '874113', 'contid': '26', 'nomer': '1',
         'fileAttached': False},
        {'name': 'КНФП 2', 'testName': 'Контрольные нормативы физической подготовленности. №2', 'weekNumber': '13',
         'currentPoints': '0', 'maxPoints': '10', 'vblid': '874113', 'contid': '26', 'nomer': '2',
         'fileAttached': False}]}], 'truancy': {'all': None, 'justified': None}}}

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