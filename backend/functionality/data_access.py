"""
This file includes all database interactions. 
"""

# import bcrypt
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

    def get_location(self):
        cursor = self.conn.cursor()

        query = "SELECT LocationCity FROM event"
        cursor.execute(query)

        result_set = cursor.fetchall()
        location_list = [row[0] for row in result_set]
        self.conn.close()

        return location_list