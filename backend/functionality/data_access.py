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
