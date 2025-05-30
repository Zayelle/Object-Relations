import os
import sqlite3

DB_PATH = os.getenv('SQLITE_DB_PATH', 'articles.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
