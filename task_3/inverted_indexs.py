import os
import re
import collections
import ssl

import nltk
import pymorphy3

from bs4 import BeautifulSoup

# Пути до папки с html страницами и файлов
SOURCE_DIR = '../task_1/pages'
INDEX_OUTPUT = './inverted_indexs.txt'

# Кодировка
ENCODING = 'utf-8'
LANG_RUSSIAN = 'russian'


def extract_text_from_html(directory_path):
    """Чтение и извлечение текста из HTML файла"""
    full_text = []
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        with open(file_path, 'r', encoding=ENCODING) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            full_text.append(' '.join(soup.stripped_strings))
    return full_text


def process_text_data(directory, tokenizer, stop_words_set, morph_analyzer):
    """Обработка текста: токенизация, лемматизация и фильтрация"""
    inverted_index = collections.defaultdict(set)

    documents = extract_text_from_html(directory)

    for doc_id, raw_text in enumerate(documents, start=1):
        tokens_in_text = tokenizer.tokenize(raw_text)

        for token in tokens_in_text:
            lower_token = token.lower()
            if len(lower_token) < 2 or lower_token in stop_words_set:
                continue

            parsed_token = morph_analyzer.parse(lower_token)
            is_digit = bool(re.compile(r'^[0-9]+$').match(lower_token))
            is_russian = bool(re.compile(r'^[а-яА-Я]{2,}$').match(lower_token))

            if not is_russian or is_digit:
                continue

            # Добавление токена в инвертированный индекс
            inverted_index[lower_token].add(doc_id)

    return inverted_index


def save_inverted_index_to_file(inverted_index, index_file):
    """Сохраняет инвертированный индекс в файл"""
    with open(index_file, 'w', encoding=ENCODING) as file:
        for term, doc_ids in inverted_index.items():
            file.write(f'{term} {" ".join(map(str, doc_ids))}\n')


def main():
    # Настройка SSL для загрузки без проверок сертификатов
    ssl._create_default_https_context = ssl._create_unverified_context

    # Загрузка ресурсов из библиотеки NLTK
    nltk.download('stopwords')

    # Инициализация объектов для обработки текста
    stop_words = set(nltk.corpus.stopwords.words(LANG_RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morph_analyzer = pymorphy3.MorphAnalyzer()

    # Обрабатываем текста и сохраняем инвертированный индекс в файл
    inverted_index = process_text_data(SOURCE_DIR, tokenizer, stop_words, morph_analyzer)
    save_inverted_index_to_file(inverted_index, INDEX_OUTPUT)


if __name__ == '__main__':
    main()
