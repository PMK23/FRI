import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Глобальный список для хранения уже обработанных задач
processed_tasks = set()

def load_processed_tasks():
    # Теперь просто возвращаем глобальный список
    return processed_tasks

def save_processed_task(task_link):
    # Добавляем задачу в глобальный список
    processed_tasks.add(task_link)

def parse_habr_freelance():
    url = "https://freelance.habr.com/tasks?categories=development_bots,development_scripts,testing_sites,testing_mobile,testing_software,other_audit_analytics,other_consulting,other_jurisprudence,other_accounting,other_audio,other_video,other_engineering,other_other"
    response = requests.get(url)

    if response.status_code != 200:
        print("Не удалось получить веб-страницу")
        return

    soup = BeautifulSoup(response.content, 'lxml')
    task = soup.find('li', class_='content-list__item')

    processed_tasks = load_processed_tasks()

    if task:
        title_tag = task.find('div', class_='task__title').find('a')
        title = title_tag.text.strip() if title_tag else 'Н/Д'
        link = 'https://freelance.habr.com' + title_tag['href'] if title_tag else 'Н/Д'

        if link in processed_tasks:
            print("Задача уже обработана")
            return

        responses_tag = task.find('span', class_='params__responses icon_task_responses')
        responses_count = responses_tag.find('i', class_='params__count').text.strip() if responses_tag else 'Н/Д'

        views_tag = task.find('span', class_='params__views icon_task_views')
        views_count = views_tag.find('i', class_='params__count').text.strip() if views_tag else 'Н/Д'

        published_tag = task.find('span', class_='params__published-at icon_task_publish_at')
        published_date = published_tag.text.strip() if published_tag else 'Н/Д'

        # Use the provided CSS selector to find the price
        price_tag = task.select_one('li.content-list__item:nth-child(1) > article:nth-child(1) > aside:nth-child(2) > div:nth-child(1) > span')
        price = price_tag.text.strip() if price_tag else 'Н/Д'

        message = (f"Название: {title}\n"
                   f"{link}\n"
                   f"Отклики: {responses_count}\n"
                   f"Просмотры: {views_count}\n"
                   f"Опубликовано: {published_date}\n"
                   f"Цена: {price}\n")

        print(message)
        send_message(message)

        save_processed_task(link)
    else:
        print("Задачи не найдены")

def send_message(message):
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

    params = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': message
    }

    res = requests.get(url, params=params)
    return res.json()

if __name__ == '__main__':
    parse_habr_freelance()