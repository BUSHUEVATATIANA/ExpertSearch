from scripts.preprocessing import preproceccing_data
from scripts.preprocess_text import preprocess_text
from sentence_transformers import SentenceTransformer
import pandas as pd
import re
import os
import emoji
import spacy 
from sklearn.model_selection import train_test_split
import numpy as np
from matplotlib import pyplot as plt
from evidently import Dataset, DataDefinition, Report, MulticlassClassification
from evidently.presets import DataSummaryPreset
from evidently.presets import *
from evidently.metrics import *
from evidently.tests import *
from evidently.descriptors import *
from evidently.ui.workspace import CloudWorkspace
from xgboost import XGBClassifier
import pickle
from scripts.get_embeddings import Get_embeddings

currency_here = os.path.dirname(__file__)
data_path = os.path.join(currency_here, "test_data.csv")
test_data = pd.read_csv(data_path)

def sent_report(data):
    ws = CloudWorkspace( token="dG9rbgGHaEAXA3xGaqO0fqQ1Rssha5BOk+sumzadpEKOaA7sPgBQVJSoBKw5aD+MX0VPnJHCV0gaWd6WZjQ9fIT40StjL892Tx6UfbSbxGV7AeLRwSHs1axB5pDcaX5rl2bDKejLZGS2xxMffNd4QPzvzaqlXAKkkXmC",
    url="https://app.evidently.cloud")
    project = ws.get_project("0196f7ce-3f64-736f-978e-d3e2d49d3418")
    data_def = DataDefinition(
    classification=[MulticlassClassification(
        target="Оценка",
        prediction_labels="prediction"
    )],
    text_columns= ['message.text']
    )
    eval_data_1 = Dataset.from_pandas(
    pd.DataFrame(data),
    data_definition=data_def
    )
    eval_data_2 = Dataset.from_pandas(
    pd.DataFrame(test_data),
    data_definition=data_def
    )
    my_eval = report.run(eval_data_1, eval_data_2)
    ws.add_run('0196f7ce-3f64-736f-978e-d3e2d49d3418', my_eval, include_data=True)

class Get_embeddings:
    def __init__(self):
        self.model = SentenceTransformer('/opt/airflow/dags/scripts/st_ft_epoch100')
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        train_embeddings  = list(model.encode(X))
        return train_embeddings

def load_model():
    here = os.path.dirname(__file__)
    model_path = os.path.join(here, "xgb_model.pkl")
    with open(model_path, "rb") as f:
        mdl = pickle.load(f)
    return mdl

def evaluate_model(df):
    data = preproceccing_data(df)
    data['message.text'] = X['О себе'].astype(str) + ' ' + 'Обязанности: ' +  data['Обязанности'].astype(str)+ ' ' + 'Компания: ' +      data['Компания'].astype(str) + ' ' + 'Учебные заведения: ' + data['Учебные заведения'].astype(str) + ' ' + 'Стаж работы: ' + data['Стаж  работы'].astype(str) + ' ' + 'Образование: ' + data['Образование'].astype(str)
    data = data.apply(preprocess_text)
    model = load_model()
    data['Оценка'] = model.predict(data)
    sent_report(data)
    return data 
