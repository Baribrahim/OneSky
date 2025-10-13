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
            



    """Authentication Methods"""
    def create_user(self, email, password, FirstName, LastName):
        with self.conn.cursor() as cursor:
            print("DATA ACCESS: adding user to database")
            cursor.execute(
                "INSERT INTO User (Email, Password, FirstName, LastName) VALUES (%s, %s, %s, %s)",
                (email, password, FirstName, LastName)
            )
            print("DATA ACCESS: added user to database")
            self.conn.commit()
    
    def user_exists(self, email):
        """Check if a user with this email already exists."""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM user WHERE Email = %s LIMIT 1", (email,))
            return cursor.fetchone() is not None
    
    
    def get_user_by_email(self, email):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM user WHERE Email = %s LIMIT 1", (email,))
            return cursor.fetchone()

    def verify_user_by_password(self, email, password):
        da = DataAccess()
        user = da.get_user_by_email(email)
        if not user:
            return None

        stored_hashed = user["Password"].encode("utf-8") if isinstance(user["Password"], str) else user["Password"]
        if bcrypt.checkpw(password.encode("utf-8"), stored_hashed):
            return user  # return full user dict (Email, FirstName, etc.)
        return None

    
    def get_event_details(self):
        with self.conn.cursor() as cursor:
            cursor.execute("select ID, Title, About from Event")
            return cursor.fetchall(), [col[0] for col in cursor.description]
    
    """Gets the users id by querying the table by email"""
    def get_id_by_email(self, email):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT ID FROM User WHERE Email = %s", (email,))
            result = cursor.fetchone()
            return result[0] if result else None

    """Stores the user id and corresponding event id in database"""
    def store_user_event_id(self, user_email, event_id):
        user_id = self.get_id_by_email(user_email)
        with self.conn.cursor() as cursor:
            cursor.execute("INSERT INTO EventRegistration (UserID, EventID) VALUES (%s, %s)", (user_id, event_id))
            self.conn.commit()