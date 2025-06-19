import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import re
import string
import os
from scripts.my_perplexity_metric import MyPerplexityMetric
from openai import OpenAI
import json
import time
from sklearn.metrics import accuracy_score, f1_score
import math
from collections import Counter
from evidently import Dataset, DataDefinition, Report
from evidently.presets import DataSummaryPreset
from evidently.presets import *
from evidently.metrics import *
from evidently.tests import *
from evidently.descriptors import *
from evidently.ui.workspace import CloudWorkspace
from evidently.core.report import Context
from evidently.core.metric_types import SingleValue
from evidently.core.metric_types import SingleValueMetric
from evidently.core.metric_types import SingleValueCalculation
from evidently.core.metric_types import BoundTest
from evidently.tests import Reference, eq

from evidently.legacy.renderers.html_widgets import plotly_figure

from typing import Optional
from typing import List
from plotly.express import line
import plotly.express as px

currency_here = os.path.dirname(__file__)
data_path = os.path.join(currency_here, "data_others.csv")
test_data = pd.read_csv(data_path)

project_id = PROJECT_ID
evi_token = EI_TOKEN
api_key = DEEPSEEK_KEY
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def sent_report(data):
  ws = CloudWorkspace(
token=evi_token,
url="https://app.evidently.cloud")
  project = ws.get_project(project_id)
  data_definition=DataDefinition(text_columns=["num",'description', 'sum_review', 'review'],
    numerical_descriptors=["rate", "fake_rating", 'perplexity_avg'],
    id_column = 'num')
  descriptors=[
        TextLength("description", alias="Length"),
        DeclineLLMEval("fake_rating", alias="Denials")]
  eval_dataset1 = Dataset.from_pandas(data, data_definition=data_definition)
  eval_dataset2 = Dataset.from_pandas(test_data,data_definition=data_definition)
  perplexity_metric = MyPerplexityMetric(column='perplexity_avg')
  report = Report([
    perplexity_metric,
    DataDriftPreset()
    ])
  my_eval = report.run(eval_dataset1, eval_dataset2)
  ws.add_run(prodject_id, my_eval, include_data=True)


def compute_perplexity_from_logprob_objs(token_logprob_objs) -> float:
    """
    Принимает на вход список объектов ChatCompletionTokenLogprob
    и возвращает перплексити.
    """
    # Извлекаем все logprob (отбрасываем None)
    logps = [obj.logprob for obj in token_logprob_objs if obj.logprob is not None]
    if not logps:
        raise ValueError("Нет доступных logprob для расчёта perplexity")

    # Сумма отрицательных логарифмов
    neg_log_sum = -sum(logps)
    N = len(logps)

    # Перплексити
    ppl = math.exp(neg_log_sum / N)
    return ppl
def deep_seekgpt(messages,temperature):
  response = client.chat.completions.create(
      model="deepseek-chat",
      messages=messages,
      temperature=temperature,
      logprobs = True,
      top_logprobs = 10,
  )
  perplexity = compute_perplexity_from_logprob_objs(response.choices[0].logprobs.content)
  content = response.choices[0].message.content
  return perplexity, content
def get_answer(data, temperature):
  predict = {}
  perpleaxity = {}

  for i, review in enumerate(data['review']):
    messages = [{"role": "user", "content": f"Here are the reviews you need to analyze:\n\n<reviews>\n{review}\n</reviews>\n\nYou are a specialist working for a reputation management agency. \n\
                Your task is to evaluate whether the reviews for a service provider on a website are fake or genuine.\n\
                You will analyze the reviews and rate them on a scale from 1 to 5, where 1 means definitely not fake, and 5 means definitely fake.\n\
                Important: The reviews are in Russian. Analyze them in their original language.\n\nToday's date is May 7, 2025. If a year is not specified in a review, assume it is the current year.\n\
                When analyzing the reviews, consider the following main indicators of fake reviews:\n\n1. Similar writing style across multiple reviews\n2. Promotional tone \n\
                3. Excessive enthusiasm with little specific detail\n4. Reviews posted at similar times\n5. Impersonal descriptions \n\
                6. Exclusively positive feedback\n\nExamples of indicators in Russian:\n\
                - Overuse of superlatives: \"лучший\", \"превосходный\", \"непревзойденный\"\n- Generic praise: \"отличный продукт\", \"рекомендую всем\" \n\
                - Lack of personal experience: \"товар супер\", без конкретных деталей\n\nIn your analysis, consider the overall tone, specificity of details, variety in writing styles, \n\
                  and distribution of positive and negative comments. Compare the reviews to the examples of fake and genuine reviews provided earlier.\n\
                  Consider the following steps:\n\n1. Count the total number of reviews and note their dates.\n2. Identify any patterns in writing style across the reviews. \n\
                  3. Assess the level of detail and personal experience in each review.\n\
                  4. Check for an unusually high concentration of positive feedback. Count positive, negative, and neutral reviews.\n\
                  5. Look for any time-related patterns in the posting of reviews. Note any suspicious clusters of reviews posted at similar times.\n6. Evaluate the authenticity of the language used. \n\
                  After your analysis, provide your reasoning for why you believe the reviews are fake or genuine. Consider specific examples from the reviews that support your conclusion.\n\
                  Finally, rate the reviews on the scale from 1 to 5, where:\n1 - Definitely not fake\n2 - Probably not fake\n3 - Uncertain\n4 - Probably fake\n5 - Definitely fake\n\
                  Present your response in the following format: Your numerical rating from 1 to 5. Please answer like one number of general rating, dont use text. \n\
                  Please proceed with your analysis and evaluation of the provided reviews."}]
    answer = deep_seekgpt(messages, temperature=temperature)
    perpleaxity[i] = answer[0]
    predict[i] = answer[1]
    time.sleep(3)

  perplexity = pd.DataFrame.from_dict(perpleaxity, orient='index', columns=['perplexity'])
  predict = pd.DataFrame.from_dict(predict, orient='index', columns=['prediction'])
  avg_perplexity = perplexity['perplexity'].mean()
  return predict, perplexity, avg_perplexity

def evaluate_model_api(data):
  for col in ['rate', 'fake_rating']:
    # Convert the column to numeric, coercing errors to NaN
    data[col] = pd.to_numeric(data[col], errors='coerce')

  api_key = 'API KEY'
  client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

  """# 1 проход"""
  predict, perplexity, avg_perplexity = get_answer(data, temperature=0.5)
  predict1, perplexity1, avg_perplexity1 = get_answer(data, temperature=0.2)
  predict2, perplexity2, avg_perplexity2 = get_answer(data, temperature=0.8)
  predict3, perplexity3, avg_perplexity3 = get_answer(data, temperature=1)
  predict4, perplexity4, avg_perplexity4 = get_answer(data, temperature=1.5)
 
  perplexity = pd.concat([perplexity, perplexity1, perplexity2, perplexity3, perplexity4], axis=1)
  predict = pd.concat([predict, predict1, predict2, predict3, predict4],axis=1)

  predict.columns = [f'predictions_{i}' for i in range(len(predict.columns))]
  perplexity.columns = [f'perplexity_{i}' for i in range(len(perplexity.columns))]

  majority_vote = {}
  for i,v in predict.iterrows():
    majority_vote[i] = Counter(v).most_common(1)[0][0]

  data["fake_rating"] = pd.DataFrame.from_dict(majority_vote, orient='index')
  data['fake_rating'] = pd.to_numeric(data['fake_rating'], errors='coerce')
  perplexity_avg = perplexity.mean(axis=1)
  data['perplexity_avg'] = perplexity_avg
  sent_report(data)
  return data

