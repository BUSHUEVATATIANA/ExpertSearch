from airflow.decorators import dag, task
from datetime import datetime, timedelta

from scripts.parse_data import data_pars
from scripts.evaluate_model import evaluate_model
from scripts.load_to_db import load_to_db 
# --- 1. Общие параметры DAG и задачи ---
default_args = {
    'owner': 'Bushueva Tatiana',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': True,
}

# --- 2. Определение DAG с TaskFlow API ---
@dag(
    dag_id='etl_pipeline',
    default_args=default_args,
    description='ETL: парсинг → модель → загрузка в БД',
    schedule_interval='@weekly',  # cron или preset
    start_date=datetime(2025, 5, 1),
    catchup=True,
    max_active_runs=1,
    tags=['etl', 'parser', 'model', 'db'],
)
def etl_pipeline():

    @task
    def parse_data():
        """
        Собираем сырые данные и возвращаем их
        """
        parsed = data_pars(
            'https://www.avito.ru/all/rezume?cd=1&q=%D0%BA%D0%BE%D1%81%D0%BC%D0%B5%D1%82%D0%BE%D0%BB%D0%BE%D0%B3+%D1%80%D0%B5%D0%B7%D1%8E%D0%BC%D0%B5'
        )
        return parsed

    @task
    def evaluate_model_task(parsed):
        """
        Оцениваем моделью и возвращаем результаты
        """
        results = evaluate_model(parsed_data)
        return results

    @task
    def load_to_db_task(results):
        """
        Загружаем результаты в базу данных
        """
        load_to_db(results)

    # Определяем порядок выполнения
    parsed = parse_data()
    evaluated = evaluate_model_task(parsed)
    load_to_db_task(evaluated)

# Экземпляр DAG
etl_pipeline()
