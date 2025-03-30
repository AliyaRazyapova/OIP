import collections
import nltk
import os
import pymorphy3
from bs4 import BeautifulSoup

# Пути до папки с html страницами и файлов
SOURCE_DIR = '../task_1/pages'
INDEX_OUTPUT = './inverted_indexs.txt'

EXCLUDED_TOKENS = {
    'NUMB', 'ROMN', 'PNCT', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'LATN', 'UNKN'
}

# Кодировка
ENCODING = 'utf-8'
LANG_RUSSIAN = 'russian'


def get_index(filename):
    """Извлечение числового идентификатор из имени файла"""
    return int(''.join(filter(str.isdigit, filename)))


def get_text(directory):
    """Считывание текста из HTML-файлов и возвращение их в виде словаря"""
    texts = collections.defaultdict(str)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        index = get_index(filename)

        with open(file_path, 'r', encoding=ENCODING) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            texts[index] = ' '.join(soup.stripped_strings)  # Извлекаем чистый текст

    return texts


def process_texts(directory, tokenizer, stop_words, morphy):
    """Обработчик HTML-файлов, токенизация, лемматизация"""
    tokens = set()
    lemmas = collections.defaultdict(set)
    indexes = collections.defaultdict(set)

    texts = get_text(directory)

    for index in sorted(texts.keys()):
        words = tokenizer.tokenize(texts[index])  # Токенизация текста

        for word in words:
            word = word.lower()

            if len(word) < 2 or word in stop_words:
                continue  # Пропускаем короткие слова и стоп-слова

            morph = morphy.parse(word)
            if any(tag in morph[0].tag for tag in EXCLUDED_TOKENS):
                continue  # Пропускаем ненужные части речи

            tokens.add(word)

            if morph[0].score >= 0.5:
                lemma = morph[0].normal_form
                lemmas[lemma].add(word)
                indexes[lemma].add(index)

    return tokens, lemmas, indexes


def save_indexes(indexes, filename):
    """Сохранение построенных индексов в файл"""
    with open(filename, 'w', encoding=ENCODING) as file:
        for lemma, index_set in sorted(indexes.items()):
            file.write(f'{lemma} {" ".join(map(str, sorted(index_set)))}\n')


def main():
    nltk.download('stopwords')
    stop_words = set(nltk.corpus.stopwords.words(LANG_RUSSIAN))
    tokenizer = nltk.tokenize.WordPunctTokenizer()
    morphy = pymorphy3.MorphAnalyzer()

    tokens, lemmas, indexes = process_texts(SOURCE_DIR, tokenizer, stop_words, morphy)
    save_indexes(indexes, INDEX_OUTPUT)


if __name__ == '__main__':
    main()
