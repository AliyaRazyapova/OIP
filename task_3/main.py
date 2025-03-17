import collections
import pymorphy3

# Пути до файлов с индексами
INDEX = '../task_1/index.txt'  # Файл с URL
INDEXS = './inverted_indexs.txt'  # Файл с инвертированным индексом

# Кодировка
UTF_8 = 'utf-8'

# Операторы для запросов
AND = 'and'
OR = 'or'
NOT = 'not'


def init_indexes():
    """Инициализация и загрузка инвертированных индексов и URL-ов"""
    all_indexes = set()  # Множество всех индексов
    lemma_indexes = collections.defaultdict(set)  # Индексы для лемм

    # Загружаем инвертированные индексы из файла
    with open(INDEXS, 'r', encoding=UTF_8) as file:
        lines = file.readlines()
        for line in lines:
            elements = line.split()
            if len(elements) > 1:
                key = elements[0]
                indexes = set(elements[1:])
                all_indexes = all_indexes.union(indexes)  # Объединяем все индексы
                lemma_indexes[key] = indexes  # Сохраняем для каждой леммы связанные индексы

    # Загружаем URL-ы из файла
    urls = collections.defaultdict(str)
    with open(INDEX, 'r', encoding=UTF_8) as file:
        lines = file.readlines()
        for line in lines:
            elements = line.split()
            if len(elements) == 2:
                key = elements[0]
                url = elements[1]
                urls[key] = url

    return lemma_indexes, urls, all_indexes


def normalize_word(morphy, word):
    """Нормализация слова (получение леммы)"""
    return morphy.parse(word)[0].normal_form


def process_query(datas, all_indexes):
    """Обработка логического запроса и вычисление результата"""
    result = set()  # Множество для хранения результата
    processing = []  # Список для промежуточных результатов
    is_need_invert = False  # Флаг инвертирования для NOT

    for i in range(len(datas)):
        if datas[i] != NOT:
            if is_need_invert:
                processing.append(all_indexes.difference(datas[i]))  # Инвертируем множества
            else:
                processing.append(datas[i])  # Добавляем в список без изменений
            is_need_invert = False
        else:
            is_need_invert = not is_need_invert  # Переключаем флаг инвертирования

    for i in range(len(processing)):
        if i == 0:
            result = result.union(processing[i])  # Объединяем первое множество
        elif i % 2 == 1:
            if processing[i] == AND:
                result = result.intersection(processing[i + 1])  # Пересечение для AND
            elif processing[i] == OR:
                result = result.union(processing[i + 1])  # Объединение для OR

    return result


def search_query(morphy, query, lemma_indexes, all_indexes):
    """Поиск по запросу, с учетом лемм и логических операторов"""
    query = query.replace('(', ' ( ').replace(')', ' ) ').split()  # Разделяем запрос на слова

    stack = []
    result = []

    for word in query:
        word = word.lower()  # Приводим все слова к нижнему регистру
        if word == '(':
            stack.append(result)  # Старт новой вложенности
            result = []
        elif word == ')':
            processed = process_query(result, all_indexes)  # Обработка вложенного запроса
            result = stack.pop()  # Возвращаемся к предыдущему уровню вложенности
            result.append(processed)
        else:
            if word != AND and word != OR and word != NOT:  # Если не логический оператор
                normalized = normalize_word(morphy, word)  # Нормализуем слово (получаем лемму)
                result.append(lemma_indexes[normalized])  # Добавляем леммы к результату
            else:
                result.append(word)  # Логический оператор, добавляем его

    return process_query(result, all_indexes)  # Финальная обработка запроса


def main():
    lemma_indexes, urls, all_indexes = init_indexes()  # Инициализируем индексы и URL-ы
    morphy = pymorphy3.MorphAnalyzer()  # Инициализация морфологического анализатора

    while True:
        query = input('Введите ваш запрос: ')  # Ввод запроса
        indexes = search_query(morphy, query, lemma_indexes, all_indexes)  # Поиск по запросу
        for index in indexes:
            print(urls.get(index))  # Выводим URL для каждого найденного индекса


if __name__ == '__main__':
    main()
