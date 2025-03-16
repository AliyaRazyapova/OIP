import os
import requests
from zipfile import ZipFile
from bs4 import BeautifulSoup

# Основной сайт и раздел новостей
BASE_URL = 'https://www.banki.ru'
NEWS_SECTION = '/news/'
NEWS_URL = BASE_URL + NEWS_SECTION
HTML_SUFFIX = '.html'

# Кодировка и папки для файлов
ENCODING = 'utf-8'
HTML_FOLDER = './pages'
INDEX_FILE = './index.txt'
ZIP_FILE = './выкачка.zip'

UNWANTED_TAGS = ['script', 'link', 'style']


def process_response(response, tags_to_remove, folder, index):
    """Обрабатывает ответ от сервера, удаляет нежелательные теги и сохраняет HTML файл"""
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Удаляем нежелательные теги
        for tag in tags_to_remove:
            for unwanted_tag in soup.find_all(tag):
                unwanted_tag.extract()

        # Формируем имя файла и сохраняем
        file_path = os.path.join(folder, f'выкачка_{index}.html')
        with open(file_path, 'w', encoding=ENCODING) as file:
            file.write(soup.prettify())
        return True
    return False


def fetch_news_links():
    """Получает ссылки на новости"""
    response = requests.get(NEWS_URL)
    links = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Находим все ссылки на новости
        links = [BASE_URL + link.get('href') for link in soup.find_all('a', href=True) if link.get('href').startswith(NEWS_SECTION)]
    return links[:100]  # Первые 100 страниц


def main():
    # Получаем ссылки на новости
    news_links = fetch_news_links()

    # Создаем папку для хранения HTML файлов
    if not os.path.exists(HTML_FOLDER):
        os.makedirs(HTML_FOLDER)

    # Записываем ссылки в индексный файл
    with open(INDEX_FILE, 'w') as index_file:
        for i, url in enumerate(news_links, start=1):
            response = requests.get(url)
            if process_response(response, UNWANTED_TAGS, HTML_FOLDER, i):
                index_file.write(f'{i} {url}\n')

    # Архивируем полученные HTML файлы
    with ZipFile(ZIP_FILE, 'w') as zip_archive:
        for root, _, files in os.walk(HTML_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                zip_archive.write(file_path, os.path.relpath(file_path, HTML_FOLDER))


if __name__ == '__main__':
    main()
