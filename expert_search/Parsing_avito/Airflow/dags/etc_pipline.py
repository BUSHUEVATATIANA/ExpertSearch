from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# Импорт ваших функций
from scripts.parse_data import data_pars
from scripts.evaluate_model import evaluate_model
from scripts.load_to_db import load_to_db 

# --- 1. Дефолтные аргументы DAG ---
default_args = {
    'owner': 'Bushueva Tatiana',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': True,
}

# --- 2. Определение DAG ---
with DAG(
    dag_id='etl_pipeline',
    default_args=default_args,
    description='ETL: парсинг → модель → загрузка в БД',
    schedule_interval='@weekly',  # можно задать cron-выражение
    catchup=False,
    max_active_runs=1,
    tags=['etl', 'parser', 'model', 'db'],
) as dag:

    # --- 3. Задачи ---

    def _parse(**context):
        """
        Собираем сырые данные и пушим в XCom
        """
        parsed = data_pars('https://www.avito.ru/all/rezume?cd=1&q=%D0%BA%D0%BE%D1%81%D0%BC%D0%B5%D1%82%D0%BE%D0%BB%D0%BE%D0%B3+%D1%80%D0%B5%D0%B7%D1%8E%D0%BC%D0%B5')
        # кладём результат в XCom для передачи дальше
        context['ti'].xcom_push(key='parsed_data', value=parsed)

    parse_task = PythonOperator(
        task_id='parse_data',
        python_callable=_parse,
        provide_context=True,
    )

    def _evaluate(**context):
        """
        Берём данные из XCom, оцениваем моделью,
        кладём результат обратно в XCom
        """
        parsed = context['ti'].xcom_pull(key='parsed_data', task_ids='parse_data')
        results = evaluate_model(parsed)
        context['ti'].xcom_push(key='evaluation_results', value=results)

    evaluate_task = PythonOperator(
        task_id='evaluate_model',
        python_callable=_evaluate,
        provide_context=True,
    )

    def _load(**context):
        """
        Берём результаты из XCom и загружаем в БД
        """
        results = context['ti'].xcom_pull(key='evaluation_results', task_ids='evaluate_model')
        load_to_db(results)

    load_task = PythonOperator(
        task_id='load_to_db',
        python_callable=_load,
        provide_context=True,
    )

    # --- 4. Описываем порядок выполнения ---
    parse_task >> evaluate_task >> load_task