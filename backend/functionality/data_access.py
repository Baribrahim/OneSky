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


    def get_connection(self):
        return pymysql.connect(
            host=self.DB_HOST,
            user=self.DB_USER,
            database=self.DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_location(self):
        location_list = []
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT LocationCity FROM event"
                    cursor.execute(query)
                    result_set = cursor.fetchall()
                    location_list = sorted(set(row['LocationCity'] for row in result_set if row ['LocationCity']))
                    cursor.close()
        except pymysql.MySQLError as e:
            print(f"Database error in get_location: {e} ")
        return location_list
    

    def get_all_events(self, location=None):
        event_list = []
        try:
            with self.get_connection() as conn:
                with conn.cursor () as cursor:
                    if location:
                        query = """
                        SELECT event.ID, event.Title, event.About, event.Date, event.StartTime, event.EndTime, event.LocationCity, event.Address, event.Capacity, Cause.Name as CauseName, Tag.TagName as TagName
                        FROM event 
                        JOIN Cause ON event.CauseID = Cause.ID
                        JOIN CauseTag ON Cause.ID = CauseTag.CauseID
                        JOIN Tag ON CauseTag.TagID = Tag.ID
                        WHERE LocationCity = %s"""
                        cursor.execute(query, (location,))
                    else:
                        query = """
                        SELECT event.ID, event.Title, event.About, event.Date, event.StartTime, event.EndTime, event.LocationCity, event.Address, event.Capacity, Cause.Name as CauseName, GROUP_CONCAT(Tag.TagName SEPARATOR ',') AS TagName
                        FROM event 
                        JOIN Cause ON event.CauseID = Cause.ID
                        JOIN CauseTag ON Cause.ID = CauseTag.CauseID
                        JOIN Tag ON CauseTag.TagID = Tag.ID
                        ORDER BY Event.Date ASC"""
                        cursor.execute(query)
                    result_set = cursor.fetchall()
        
                    for item in result_set:
                        event = {
                            'ID': item['ID'],
                            'Title': item["Title"],
                            'About': item["About"],
                            'Date': item["Date"],
                            'StartTime': item["StartTime"],
                            'EndTime': item["EndTime"],
                            'LocationCity': item["LocationCity"],
                            'Address': item["Address"],
                            'Capacity': item["Capacity"],
                            'CauseName': item['CauseName'],
                            'TagName': item["TagName"]
                        }
                        event_list.append(event)
        except pymysql.MySQLError as e:
            print(f"Database error in get_all_events: {e}")
    
        return event_list

    
    
    def search_events(self, keyword=None, location=None, date=None):
        events = []
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    query = """
                        
                    SELECT e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName, GROUP_CONCAT(t.TagName SEPARATOR ', ') AS TagNames
                    FROM Event e
                    JOIN Cause c ON e.CauseID = c.ID
                    JOIN CauseTag ct ON c.ID = ct.CauseID
                    JOIN Tag t ON ct.TagID = t.ID
                    WHERE 1=1
                    """

                    params = []

                    if keyword:
                        query += " AND (e.Title LIKE %s OR e.About LIKE %s)"
                        keyword_param = f"%{keyword}%"
                        params.extend([keyword_param, keyword_param])

                    if location:
                        query += " AND LOWER(TRIM(e.LocationCity)) = %s"
                        params.append(location)

                    if date:
                        query += " AND e.Date = %s"
                        params.append(date)

                    query += " GROUP BY e.ID ORDER BY e.Date ASC"

                    print("Executing query with params:", query)

                    cursor.execute(query, params)
                    events = cursor.fetchall()

                finally:
                    cursor.close()
        except pymysql.MySQLError as e:
            print(f"Database error in search_events: {e}")
                   
        return events
            

