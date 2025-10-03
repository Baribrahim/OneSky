"""
This file includes all database interactions. 
"""

import bcrypt
from dotenv import load_dotenv
import os
import pymysql
import random

class DataAccess:

    load_dotenv()
    DB_HOST = os.getenv("MYSQL_HOST")
    DB_USER = os.getenv("MYSQL_USER")
    DB_DATABASE = os.getenv("MYSQL_DB")

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        database=DB_DATABASE
    )

    def get_event_details(self):
        with self.conn.cursor() as cursor:
            cursor.execute("select ID, Title, About from Event limit 1")
            return cursor.fetchall()

if __name__ == "__main__":

    da = DataAccess()
    print(da.get_event_details())
