import re
import emoji
import pandas as pd
import numpy as np
import spacy

nlp = spacy.load("ru_core_news_lg")
def remove_person_names(text: str) -> str:
    """
    Удаляет из текста все сущности типа PER (Person).
    """
    doc = nlp(text)
    for ent in reversed(doc.ents):
        if ent.label_ == "PER":
            text = text[:ent.start_char] + text[ent.end_char:]
    return text

def latin_to_cyrillic(text):
    # Словарь соответствий: латинские -> кириллические
    mapping = {
        'A': 'А', 'a': 'а',
        'e': 'е',
        'b': 'в', 'k': 'к',
        'k': 'к', 'h': 'н',
        'O': 'О', 'o': 'о',
        'P': 'Р', 'C': 'С', 'c': 'с',
        'T': 'Т', 'X': 'Х',
        'y': 'у', 'Y': 'У',
        'x': 'х',
        'r': 'г', 
        'n': 'п',  
        'i': 'и',
        'm': 'м',
        'l': 'л',
        'd': 'д',
        's': 'с',
        'u': 'и',  
        'z': 'з',
    }

    return ''.join(mapping.get(char, char) for char in text)
def convert_emojis_to_words(text):

    # Convert emojis to words
    text = emoji.replace_emoji(text, replace="")

    # Remove the : from the words and replace _ with space
    text = text.replace("_", " ")

    return text
symbols_pattern = re.compile(pattern = "["
    "@_!#$%^&*()<>?/\|}{~√•—"
                       "]+", flags = re.UNICODE) #спецсимволы
# двойные пробелы
space_pattern = re.compile('\s+')
def clear_text(text):
    """ Функция удаления спецсимволов"""
    # удаление спецсимволов и emoji
    pre = symbols_pattern.sub(r'',text)
    pre1 = convert_emojis_to_words(pre)

    return space_pattern.sub(' ', pre1)
def preprocess_text(text):
    """ Финальная функция для обработки """
    # srip + lower + punctuation
    sentence = (
        ''.join([x for x in str(text).strip().lower()])
    )

    sentence = latin_to_cyrillic(sentence)
    sentence = remove_person_names(sentence)
    return clear_text(sentence)