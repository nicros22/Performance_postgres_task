FROM python:3.11

RUN pip install psycopg2-binary python-dotenv

WORKDIR /app
COPY . /app
COPY data/postgres.env /app