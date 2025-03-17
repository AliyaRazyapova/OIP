import os
import re
import collections
import ssl

import nltk
import pymorphy3

from bs4 import BeautifulSoup

# Пути до папки с html страницами и файлов
SOURCE_DIR = '../task_1/pages'
TOKEN_OUTPUT = './tokens.txt'
LEMMA_OUTPUT = './lemmas.txt'

EXCLUDED_TOKENS = {
    'NUMB', 'NUMB,intg', 'ROMN', 'PNCT', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'LATN', 'UNKN'
}

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
    return ' '.join(full_text)


def process_text_data(directory, tokenizer, stop_words_set, morph_analyzer):
    """Обработка текста: токенизация, лемматизация и фильтрация"""
    valid_tokens = set()
    token_lemmas = collections.defaultdict(set)

    raw_text = extract_text_from_html(directory)
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

        valid_tokens.add(lower_token)
        if parsed_token[0].score >= 0.5:
            token_lemmas[parsed_token[0].normal_form].add(lower_token)

    return valid_tokens, token_lemmas


def save_tokens_and_lemmas_to_file(tokens_set, lemmas_dict, tokens_file, lemmas_file):
    """Сохраняет токены и леммы в файлы"""

    # Сохраняем токены
    with open(tokens_file, 'w', encoding=ENCODING) as token_file:
        token_file.write('\n'.join(tokens_set) + '\n')

    # Сохраняем леммы
    with open(lemmas_file, 'w', encoding=ENCODING) as lemma_file:
        for lemma, tokens in lemmas_dict.items():
            lemma_file.write(f'{lemma} {" ".join(tokens)}\n')


def main():
    # Настройка SSL для загрузки без проверок сертификатов
    ssl._create_default_https_context = ssl._create_unverified_context

    # Загрузка ресурсов из библиотеки NLTK
    nltk.download('stopwords')

    # Инициализация объектов для обработки текста
    stop_words = set(nltk.corpus.stopwords.words(LANG_RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morph_analyzer = pymorphy3.MorphAnalyzer()

    # Обрабатываем текста и сохраняем результаты в файлы
    tokens, lemmas = process_text_data(SOURCE_DIR, tokenizer, stop_words, morph_analyzer)
    save_tokens_and_lemmas_to_file(tokens, lemmas, TOKEN_OUTPUT, LEMMA_OUTPUT)


if __name__ == '__main__':
    main()
