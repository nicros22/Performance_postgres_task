import os
from dotenv import load_dotenv
import argparse
import psycopg2
import random
import string
import time
import concurrent.futures

load_dotenv()


def create_table_or_delete_if_exists():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host="postgres",
        port="5432"
    )
    cur = conn.cursor()

    # Удаление таблицы, если она уже существует
    cur.execute("DROP TABLE IF EXISTS info;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS info (
            id SERIAL PRIMARY KEY,
            data TEXT NOT NULL
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# Функция для вставки данных в PostgreSQL
def insert_data(thread_id, duration):
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host="postgres",
        port="5432"
    )
    cur = conn.cursor()

    start_time = time.time()
    end_time = start_time + duration

    while time.time() < end_time:
        random_string = ''.join(random.choices(string.ascii_lowercase, k=10))
        cur.execute("INSERT INTO INFO (data) VALUES (%s)", (random_string,))
        conn.commit()

    cur.close()
    conn.close()


# Функция для параллельного выполнения вставки данных
def main(num_threads, duration):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_thread = {executor.submit(insert_data, i, duration): i for i in range(num_threads)}
        for future in concurrent.futures.as_completed(future_to_thread):
            thread_id = future_to_thread[future]
            try:
                future.result()
            except Exception as exc:
                print(f"Thread {thread_id} generated an exception: {exc}")
    print("Insertion completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert data into PostgreSQL")
    parser.add_argument("--threads", type=int, help="Number of parallel threads", required=True)
    parser.add_argument("--duration", type=int, help="Duration of insertion in seconds", required=True)
    args = parser.parse_args()

    create_table_or_delete_if_exists()  # Создать таблицу или очистить перед вставкой данных
    main(args.threads, args.duration)
