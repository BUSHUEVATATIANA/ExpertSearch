import pandas as pd
import re
import json
from pymorphy3 import MorphAnalyzer
def find_between_strings(lst, start_str, end_str):
    result = []
    found_start = False
    lst = lst.split('\n')
    for item in lst:
        if found_start:
            if item == end_str:
                break
            result.append(item)
        elif item == start_str:
            found_start = True
    if result == []:
        return 'Не указано'
    else:
        return result
def preprocessing(df):
    text = df.lower()
    text = (
        ' '.join([
            morpher.parse(word)[0].normal_form 
            for word in text.split()]))
    return text
# Функция для преобразования строки с длительностью в месяцы
def convert_to_months(date):
    months = 0
    if 'год' in preprocessing(date):
        years = int(re.search(r'(\d+)\s*год', preprocessing(date)).group(1))
        months += years * 12
    # Если указано "месяц" или "месяцев", добавляем указанные месяцы
    if 'месяц' in preprocessing(date):
        months_part = re.search(r'(\d+)\s*месяц', preprocessing(date))
        if months_part:
            months += int(months_part.group(1))
    return months
#Функция преобразования опыта работы
def analyze_experience(df):
    total_years = 0
    cosmetologist_jobs = []
    if df == 'Не указано':
        return 'Не указано'
    else:
        i = 0
        while i < len(df):
            if i + 3 >= len(df):
                break
            months = convert_to_months(df[i])
            years = months / 12
            years = round(years,2)
            job_title = df[i + 2] # название компании
            job_describe = df[i+3] # описаие обязанностей
            job_title_lemma = preprocessing(job_title)
            for word in cosmetologist_words:
                if word in job_title_lemma:
                    cosmetologist_jobs.append(f'year*{years}; company*{job_title}; responsibilities*{job_describe}')
                    total_years += years
            i+=4
    cosmetologist_set = set(cosmetologist_jobs)
    return cosmetologist_set
#Функция разделения словаря
def process_experience(data):
    total_year = 0  # сумма всех year
    companies = set()  # компании
    responsibilities = set()  #обязанностей
    if data ==  'Не указано' or data == {}:
        return None
    else:
        for experience_str in data:
            parts = experience_str.split(';')

            year = None
            company = None
            responsibility = None

            for part in parts:
                if 'year' in part:
                    year = float(part.split('*')[1].strip())  # Извлекаем и приводим year к числу
                    total_year += year  # Добавляем к общей сумме
                elif 'company' in part:
                    company = part.split('*')[1].strip()  # Извлекаем компанию
                    companies.add(company)  # Добавляем компанию в множество
                elif 'responsibilities' in part:
                    responsibility = part.split('*')[1].strip()  # Извлекаем обязанности
                    responsibilities.add(responsibility)  # Добавляем обязанности в множество

        company_list = list(companies)
        responsibility_list = list(responsibilities)
        d = {
        'Стаж работы': total_year,
        'Компания': company_list,
        'Обязанности': responsibility_list
         }
        return d
def explode_list(data):
    if data == 'Не указано':
        return 'Не указано'
    else:
        return ','.join(data)
def get_strings_between_start(lst):
    in_between = False  # Флаг, который указывает, находимся ли мы между строками с нужными префиксами
    result = []

    for line in lst:
        # Если строка начинается с start_prefix, начинаем собирать строки
        if line.startswith('Год окончания'):
            in_between = True
            continue  # Пропускаем строку с началом "start_prefix"
        
        # Если строка начинается с end_prefix и мы находимся в промежутке, заканчиваем собирать
        if line.startswith('Знание языков') and in_between:
            in_between = False
            continue  # Пропускаем строку с началом "end_prefix"
        elif line.startswith('Гражданство') and in_between:
            in_between = False
            continue  # Пропускаем строку с началом "end_prefix"
        
        # Если мы находимся в промежутке, добавляем строку
        if in_between:
            result.append(line)
        if lst == 'Не указано':
            return 'Не указано'
    
    return ",".join(result)
def find_between_strings_for_basic(lst, start_str, end_str):
    result = []
    found_start = False
    lst = lst.split(':')
    for items in lst:
        items = items.split('\n')
        for item in items:
            if found_start:
                if item == end_str:
                    break
                result.append(item)
            elif item == start_str:
                found_start = True
    if result == []:
        return 'Не указано'
    else:
        return result[:1]
        
def preproceccing_data(json_file):
    with open(json_file, encoding='utf-8') as inputfile:
        data = pd.read_json(inputfile)
    start_word = "Опыт работы"
    end_word = "Учебные заведения"
    data["Опыт работы"] = data.table.apply(find_between_strings, args=(start_word, end_word))
    morpher = MorphAnalyzer()
    cosmetologist_words = ['косметолог','косметология', 'эстетист', 'косметолог-эстетист', 'медсестра-косметолог', 'врач',      'врач-косметолог', 'дерматовенеролог', 'лаборатория', 'лаборант']
    data['Опыт работы'] = data['Опыт работы'].apply(analyze_experience)
    result = data['Опыт работы'].apply(process_experience)
    experience = pd.json_normalize(result)
    data.reset_index(drop=True, inplace=True)
    data = pd.concat([data,experience], axis=1) #соединяем с исходным датасетом
    values = {'Стаж работы': 0,'Компания': "Не указано", 'Обязанности': "Не указано"}
    data=data.fillna(value = values)
    data['Компания'] = data['Компания'].apply(explode_list)
    data['Обязанности'] = data['Обязанности'].apply(explode_list)
    start_word = "Учебные заведения"
    end_word = "Медкнижка"
    data["Учебные заведения"] = data.table.apply(find_between_strings, args=(start_word, end_word))
    start_word = "Гражданство"
    data['Гражданство'] = data.table.apply(find_between_strings, args=(start_word, None))
    for elem in data['Гражданство']:
        if elem == ['Гражданство — Россия']:
            data['Гражданство'] = 'Россия'
        else: 
            data['Гражданство'] = 'другое'
    data['Учебные заведения'] = data["Учебные заведения"].apply(get_strings_between_start)
    start_words = ['Тип занятости', 'Сфера деятельности', 'Образование', 'Пол', 'Возраст']
    for start_word in start_words: 
        data[start_word] = data.basic.apply(find_between_strings_for_basic, args=(start_word, None)).explode().str.strip()
    data = data.rename(columns={"num": "Идентификатор на сайте", "description": "О себе"})
    data = data.drop(['table', 'basic', 'Опыт работы'], axis = 1)
    return data
if __name__ == "__main__":
    preproceccing_data(json_file)
    
    

 