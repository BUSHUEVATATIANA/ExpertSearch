import os
import psycopg2


def load_to_db(data):
    """
    Загружает предсказания модели в PostgreSQL.

    Параметры подключения берутся из переменных окружения:
      - DB_HOST
      - DB_PORT
      - DB_NAME
      - DB_USER
      - DB_PASSWORD
    """
    # Читаем параметры подключения из окружения
    host = '192.168.33.10'
    port =  '5432'
    dbname = 'cosmetologistdb'
    user = 't_user'
    password = 'qrygfrhj589jhfd'

    if not all([dbname, user, password]):
        raise ValueError("Не заданы обязательные переменные окружения для подключения к БД")

    # Устанавливаем соединение
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    if not data:
        print("Нет данных для загрузки.")
        cursor.close()
        conn.close()
        return

    # Формируем запрос на вставку динамически по ключам словаря
    columns = data[0].keys()
    col_list = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO model_predictions ({col_list}) VALUES ({placeholders})"

    # Выполняем вставку для каждой записи
    for record in data:
        values = [record[col] for col in columns]
        cursor.execute(insert_sql, values)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Загружено {len(data)} записей в таблицу model_predictions.")


if __name__ == "__main__":
    load_to_db(preds)
