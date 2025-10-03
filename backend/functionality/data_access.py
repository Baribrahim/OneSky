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
        # location_list = [row[0] for row in result_set]
        location_list = list(set(row[0] for row in result_set))  # Removes duplicates
        self.conn.close()

        return location_list
    
    
    def search_events(self, keyword=None, location=None, date=None):
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime,
                    e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName
                FROM Event e
                JOIN Cause c ON e.CauseID = c.ID
                WHERE 1=1
            """
            params = []

            if keyword:
                query += " AND (e.Title LIKE %s OR e.About LIKE %s)"
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param])

            if location:
                query += " AND e.LocationCity = %s"
                params.append(location)

            if date:
                query += " AND e.Date = %s"
                params.append(date)

            cursor.execute(query, params)
            result_set = cursor.fetchall()

            conn.close()
            return result_set
