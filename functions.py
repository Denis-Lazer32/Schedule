'''
Функции необходимые для работы программы
'''

import datetime
import requests
import dotenv
import json
import os

import operator
import jinja2


# Получение данных с vk.com
def parse_vk_data():
    # Загрузка переменных окружения
    dotenv.load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    vk_id = os.getenv('VK_ID')

    # Получение данных пользователя
    vk_path = "https://api.vk.com/method/users.get"
    vk_data = requests.get(url=vk_path, params={"access_token": vk_token,
                                                "user_ids": vk_id,
                                                "fields": 'photo_200',
                                                "v": 5.131
                                                }).json()

    # Запись в файл
    with open("vk.json", "w+", encoding="utf-8") as VK_FILE:
        json.dump(vk_data, VK_FILE, indent=4, ensure_ascii=False)

    return vk_data


# Получение данных с ruz.hse.ru
def parse_ruz_data():
    # Загрузка переменных окружения
    dotenv.load_dotenv()
    ruz_id = os.getenv("RUZ_ID")

    # Получение даты
    now = datetime.date.today()
    start = str(now)
    finish = str(now + datetime.timedelta(days=7))

    # Получение данных расписания
    ruz_path = "https://ruz.hse.ru/api/schedule/student/" + ruz_id
    ruz_data = requests.get(url=ruz_path, params={"start": start, "finish": finish}
                            ).json()

    # Запись в файл
    with open("ruz.json", "w+", encoding="utf-8") as ruz_file:
        json.dump(ruz_data, ruz_file, indent=4, ensure_ascii=False)

    return ruz_data


def receiving_html():
    # Получение данных с vk.com и ruz.hse.ru
    vk_data = parse_vk_data()
    ruz_data = parse_ruz_data()

    # Запись данных в переменные
    vk_response = vk_data['response'][0]
    first_name = vk_response['first_name']
    last_name = vk_response['last_name']
    photo = vk_response['photo_200']
    timetable = sorted(ruz_data,
                       key=operator.itemgetter("date", "beginLesson"))

    # Загрузка шаблонов html
    file_loader = jinja2.FileSystemLoader('templates')
    environment = jinja2.Environment(
        loader=file_loader)
    main_page = environment.get_template('index.html')
    schedule = environment.get_template('schedule.html')

    # Рендеринг html
    render_main_page = main_page.render(
        first_name=first_name,
        last_name=last_name,
        photo=photo)
    render_schedule = schedule.render(
        schedule=timetable)

    # Запись в файлы
    with open('your_schedule.html', mode="w", encoding='utf-8') as HTML_FILE:
        HTML_FILE.write(render_main_page)
    with open('schedule.html', mode="w", encoding='utf-8') as SCHEDULE_FILE:
        SCHEDULE_FILE.write(render_schedule)
