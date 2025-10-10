"""
This file includes all database interactions. 
"""

# import bcrypt
from dotenv import load_dotenv
import os
import pymysql
import random

class DataAccess:

# This should be in an initialization function:
    # load_dotenv()
    # DB_HOST = os.getenv("MYSQL_HOST")
    # DB_USER = os.getenv("MYSQL_USER")
    # DB_DATABASE = os.getenv("MYSQL_DB")

# This should also be a function:
    # conn = pymysql.connect(
    #     host=DB_HOST,
    #     user=DB_USER,
    #     database=DB_DATABASE
    # )

# Without having them like this it kept crashing as when we were creating a single connection
# it would time out after a while and we would have to restart the server
# By creating a new connection for each function it works fine
    def __init__(self):
        load_dotenv()
        self.DB_HOST = os.getenv("MYSQL_HOST")
        self.DB_USER = os.getenv("MYSQL_USER")
        self.DB_DATABASE = os.getenv("MYSQL_DB")
        self.conn = self.get_connection()

    def get_connection(self):
        return pymysql.connect(
            host=self.DB_HOST,
            user=self.DB_USER,
            database=self.DB_DATABASE
        )

    def get_location(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT LocationCity FROM event"
        cursor.execute(query)

        result_set = cursor.fetchall()
        # location_list = [row[0] for row in result_set]
        location_list = list(set(row[0] for row in result_set))  # Removes duplicates

        conn.close()
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
