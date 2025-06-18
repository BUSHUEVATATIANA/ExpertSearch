from scripts import preprocessing
from sentence_transformers import SentenceTransformer
import pandas as pd
import re
import os
import emoji
from sklearn.model_selection import train_test_split
import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import accuracy_score, f1_score
from sklearn.metrics import confusion_matrix
from xgboost import XGBClassifier
import wandb 
import pickle
from scripts.get_embeddings import Get_embeddings
wandb.login(key='118570a17fac7c4cffe0ad0c784f09cf67222d20')

def load_model():
    here = os.path.dirname(__file__)
    model_path = os.path.join(here, "xgb_model.pkl")
    with open(model_path, "rb") as f:
        mdl = pickle.load(f)
    return mdl
currency_here = os.path.dirname(__file__)
data_path = os.path.join(currency_here, "test_data.csv")
test_data = pd.read_csv(data_path)
y_test = test_data['Оценка']
def get_metrics(prediction):
    accuracy = accuracy_score(y_test, prediction)
    f1 = f1_score(y_test, prediction, average='weighted')
    data_metric = pd.DataFrame({'accuracy':accuracy, 'f1_score':f1})
    data_metric.to_csv('/opt/airflow/dags/scripts/data/metric.csv')
    cm = confusion_matrix(y_test, prediction, labels=np.unique(y_test))
    fig, ax = plt.subplots(figsize=(6,6))
    im = ax.imshow(cm, interpolation='nearest', aspect='auto')
    unique_labels = np.unique(y_test).astype(int)
    ax.set_xticks(range(9))
    ax.set_yticks(range(9))
    ax.set_xticklabels(unique_labels, rotation=45)
    ax.set_yticklabels(unique_labels)
    ax.set_ylabel('Истинный класс')
    ax.set_xlabel('Предсказанный класс')
    fig.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.show()
    plt.savefig('/opt/airflow/dags/scripts/data/confusion_matrix.png')
    return data_metric
def convert_emojis_to_words(text):

    # Convert emojis to words
    text = emoji.demojize(text, delimiters=(" ", " "))

    # Remove the : from the words and replace _ with space
    text = text.replace("_", " ")

    return text
def clear_text(text):
    """ Функция удаления спецсимволов"""
    symbols_pattern = re.compile(pattern = "["
    "@_!#$%^&*()<>?/\|}{~√•—"
                       "]+", flags = re.UNICODE) #спецсимволы
    # двойные пробелы
    space_pattern = re.compile('\s+')
    # удаление спецсимволов и emoji
    pre = symbols_pattern.sub(r'',text)

    return space_pattern.sub(' ', pre)
def preprocess_text(text):
    """ Финальная функция для обработки """
    # srip + lower + punctuation
    sentence = (
        ''.join([x for x in str(text).strip().lower()])
    )

    return clear_text(sentence)
def evaluate_model(data):
    wandb.init(project="my_etl_project",job_type="evaluation",config={ "num_samples": len(data)})
    X = preprocessing(data)
    X = X['О себе'].astype(str) + ' ' + 'Обязанности: ' +  X['Обязанности'].astype(str)+ ' ' + 'Компания: ' +      X['Компания'].astype(str) + ' ' + 'Учебные заведения: ' + X['Учебные заведения'].astype(str) + ' ' + 'Стаж работы: ' + X['Стаж  работы'].astype(str) + ' ' + 'Образование: ' + X['Образование'].astype(str)
    X = X.apply(preprocess_text)
    model = load_model()
    data['Оценка'] = model.predict(X)
    metrics = get_metrics(data['Оценка'])
    wandb.log(metrics)
    wandb.finish()
    return data 
