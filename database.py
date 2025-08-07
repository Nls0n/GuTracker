import psycopg2
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(
        dbname='GuTracker',
        user="postgres",
        password='A12138877',
        host='localhost'
    )
    try:
        yield conn
    finally:
        conn.close()