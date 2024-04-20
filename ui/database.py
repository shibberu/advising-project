import sys
version = sys.argv[1] # should be 'test' or 'prod'
db_name = f'db-{version}.db'

import sqlite3

def create_database():
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY,
                        query TEXT,
                        response TEXT
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()

def add_log(query, response):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO logs (query, response) VALUES (?, ?)', (query, response))
        conn.commit()

create_database()