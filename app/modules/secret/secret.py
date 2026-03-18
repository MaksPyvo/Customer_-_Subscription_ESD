import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# db connection variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# get connection to data and persistence db
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def get_secret():
    # connect to db
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # get secret for customer and subscriptions (id = 5)
        cursor.execute('SELECT * FROM dtsecrets where id = 5;')
        secret = cursor.fetchone()
        return secret
    finally:
        # close connection
        cursor.close()
        conn.close()