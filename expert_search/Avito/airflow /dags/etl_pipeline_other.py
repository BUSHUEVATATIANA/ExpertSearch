from airflow.decorators import dag, task
from datetime import datetime, timedelta
from scripts.parsed_other import data_pars
from scripts.evaluate_model_other import evaluate_model_api as evaluate_model
from scripts.load_to_vector_db import load_to_milvus 
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
    dag_id='etl_pipeline_other',
    default_args=default_args,
    description='ETL: парсинг → модель → загрузка в векторную БД',
    schedule_interval='@weekly',  # cron или preset
    start_date=datetime(2025, 6, 16),
    catchup=False,
    max_active_runs=1,
    tags=['etl_other', 'parser_other', 'model_api', 'vector_db'],
)
def etl_pipeline_other():

    @task
    def parse_data():
        """
        Собираем сырые данные и возвращаем их
        """
        parsed = data_pars(
            'https://www.avito.ru/all/predlozheniya_uslug/krasota/brovi_resnicy-ASgBAgICAkSYC6qfAaIrrOSKAw?f=ASgBAgICA0SYC6qfAaIrrOSKA566FOC~jwM&p=4&s=104'
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
        load_to_milvus(results)

    # Определяем порядок выполнения
    parsed = parse_data()
    evaluated = evaluate_model_task(parsed)
    load_to_db_task(evaluated)

# Экземпляр DAG
etl_pipeline_other()
