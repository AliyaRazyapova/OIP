import os
import math
import collections
import nltk
import pymorphy3
from bs4 import BeautifulSoup

# Пути до папки с HTML-страницами и выходных папок
SOURCE_DIR = '../task_1/pages'
TOKENS_DIR = './tokens'
LEMMAS_DIR = './lemmas'

EXCLUDED_TOKENS = {
    'NUMB', 'NUMB,intg', 'ROMN', 'PNCT', 'PREP', 'CONJ', 'PRCL', 'INTJ', 'LATN', 'UNKN'
}

# Кодировка
ENCODING = 'utf-8'
LANG_RUSSIAN = 'russian'

# Префиксы для хранения обработанных данных
TOKEN_FILE_PREFIX = './tokens/page_'
LEMMA_FILE_PREFIX = './lemmas/page_'
FILE_EXTENSION = '.txt'


class TextProcessor:
    """Токенизация и лемматизация текста с учетом морфологического анализа"""
    def __init__(self, text):
        self.text = text
        self.tokenizer = nltk.tokenize.WordPunctTokenizer()
        self.morph_analyzer = pymorphy3.MorphAnalyzer()
        self.stop_words = set(nltk.corpus.stopwords.words(LANG_RUSSIAN))
        self.tokens = []
        self.lemmas = collections.defaultdict(set)

    def process_text(self):
        """Обработка текста: токенизация, лемматизация и фильтрация"""
        for token in self.tokenizer.tokenize(self.text.lower()):
            if len(token) < 2 or token in self.stop_words:
                continue
            parsed_token = self.morph_analyzer.parse(token)[0]
            if any(tag in parsed_token.tag for tag in EXCLUDED_TOKENS):
                continue
            self.tokens.append(token)
            if parsed_token.score >= 0.5:
                self.lemmas[parsed_token.normal_form].add(token)


def extract_texts_from_html(directory):
    """Берем текст из всех HTML-файлов в указанной директории"""
    extracted_texts = {}
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        index = int(''.join(filter(str.isdigit, filename)))
        with open(file_path, 'r', encoding=ENCODING) as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            extracted_texts[index] = ' '.join(soup.stripped_strings)
    return extracted_texts


def term_frequency(term, document_tokens):
    """Вычисление частоты термина (TF) в документе"""
    return document_tokens.count(term) / len(document_tokens) if document_tokens else 0


def inverse_document_frequency(term, documents):
    """Вычисление обратной частоты документа (IDF)"""
    term_occurrences = sum(1 for text in documents.values() if term in text.lower())
    return math.log(len(documents) / (1 + term_occurrences)) if term_occurrences else 0


def save_to_file(filename, word, idf, tf_idf):
    """Сохранение результатов вычислений в файл"""
    with open(filename, 'a', encoding=ENCODING) as file:
        file.write(f"{word} {idf:.6f} {tf_idf:.6f}\n")


def create_directories():
    """Создание директории для хранения токенов и лемм, если они не существуют"""
    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)


def main():
    create_directories()
    documents = extract_texts_from_html(SOURCE_DIR)
    for doc_id, text in sorted(documents.items()):
        processor = TextProcessor(text)
        processor.process_text()
        token_counts = collections.Counter(processor.tokens)

        # Вычисляем TF-IDF для токенов
        for token in set(processor.tokens):
            tf = term_frequency(token, processor.tokens)
            idf = inverse_document_frequency(token, documents)
            save_to_file(f"{TOKEN_FILE_PREFIX}{doc_id}{FILE_EXTENSION}", token, idf, tf * idf)

        # Вычисляем TF-IDF для лемм
        for lemma, tokens in processor.lemmas.items():
            total_count = sum(token_counts[token] for token in tokens) + token_counts[lemma]
            tf = total_count / len(processor.tokens)
            idf = inverse_document_frequency(lemma, documents)
            save_to_file(f"{LEMMA_FILE_PREFIX}{doc_id}{FILE_EXTENSION}", lemma, idf, tf * idf)


if __name__ == '__main__':
    main()
