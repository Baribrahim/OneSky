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

    # conn = pymysql.connect(
    #     host=DB_HOST,
    #     user=DB_USER,
    #     database=DB_DATABASE
    # )

    def get_connection(self):
        # Short-lived connections; no global shared conn.
        return pymysql.connect(
            host=self.DB_HOST,
            user=self.DB_USER,
            database=self.DB_DATABASE,
            autocommit=True)

    print("Connected to database")

    # ------------------------
    # Authentication Methods
    # ------------------------
    def create_user(self, email, password, FirstName, LastName):
        sql = """
            INSERT INTO User (Email, Password, FirstName, LastName)
            VALUES (%s, %s, %s, %s)
        """
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(sql, (email, password, FirstName, LastName))
            # autocommit=True handles commit

    def user_exists(self, email):
        """Check if a user with this email already exists."""
        sql = "SELECT 1 FROM user WHERE Email = %s LIMIT 1"
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(sql, (email,))
            return cursor.fetchone() is not None

    def get_user_by_email(self, email):
        sql = "SELECT * FROM user WHERE Email = %s LIMIT 1"
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (email,))
            return cursor.fetchone()

    def verify_user_by_password(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return None
        stored_hashed = (
            user["Password"].encode("utf-8")
            if isinstance(user["Password"], str)
            else user["Password"]
        )
        if bcrypt.checkpw(password.encode("utf-8"), stored_hashed):
            return user  # full user dict
        return None

    # ------------------------
    # Generic Event/Data Methods
    # ------------------------
    def get_event_details(self):
        try:
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Event")
                rows = cursor.fetchall()
                cols = [col[0] for col in cursor.description]
                return rows, cols
        except Exception as e:
            print(f"Error in get_event_details: {e}")
            raise

    def get_id_by_email(self, email):
        try:
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute("SELECT ID FROM User WHERE Email = %s", (email,))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Error in get_id_by_email: {e}")
            raise

    def store_user_event_id(self, user_email, event_id):
        try:
            user_id = self.get_id_by_email(user_email)
            sql = "INSERT INTO EventRegistration (UserID, EventID) VALUES (%s, %s)"
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(sql, (user_id, event_id))
                # autocommit=True
        except Exception as e:
            print(f"Error in store_user_event_id: {e}")
            raise

    def get_user_events(self, user_email):
        try:
            user_id = self.get_id_by_email(user_email)
            sql = "SELECT EventID FROM EventRegistration WHERE UserID = %s"
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))  # NOTE the comma -> (user_id,)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error in check_user_event_signup: {e}")
            raise

    def delete_user_from_event(self, user_email, event_id):
        try:
            user_id = self.get_id_by_email(user_email)
            sql = "DELETE FROM EventRegistration WHERE UserID = %s AND EventID = %s"
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(sql, (user_id, event_id))
                # autocommit=True
        except Exception as e:
            print(f"Error in unregister_user_from_event: {e}")
            raise

    # ------------------------
    # Dashboard Methods
    # ------------------------
    def get_user_id_by_email(self, email):
        """
        Retrieve the unique user ID from the database using the user's email.
        """
        sql = "SELECT ID FROM User WHERE Email = %s LIMIT 1"
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (email,))
            row = cursor.fetchone()
            return row["ID"] if row else None

    def get_upcoming_events(self, user_id: int, limit: int = 5):
        """
        Get upcoming events a user has registered for (future only).
        """
        sql = """
            SELECT 
                e.ID,
                e.Title,
                DATE_FORMAT(e.Date, '%%Y-%%m-%%d')      AS Date,
                DATE_FORMAT(e.StartTime, '%%H:%%i:%%s') AS StartTime,
                DATE_FORMAT(e.EndTime, '%%H:%%i:%%s')   AS EndTime,
                e.LocationCity
            FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
              AND TIMESTAMP(e.Date, e.StartTime) > NOW()
            ORDER BY TIMESTAMP(e.Date, e.StartTime) ASC
            LIMIT %s
        """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id, int(limit)))
            return cursor.fetchall()
    
    def get_upcoming_events_count(self, user_id: int) -> int:
        """
        Count all future events a user has registered for (no limit).
        """
        sql = """
            SELECT COUNT(*) AS UpcomingCount
            FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
            AND TIMESTAMP(e.Date, e.StartTime) > NOW()
        """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return int(row["UpcomingCount"]) if row and row["UpcomingCount"] is not None else 0


    def get_total_hours(self, user_id: int):
        """
        Sum completed hours from past events.
        """
        sql = """
            SELECT COALESCE(SUM(TIME_TO_SEC(e.Duration)) / 3600, 0) AS TotalHours
            FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
              AND TIMESTAMP(e.Date, e.StartTime) < NOW()
        """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return float(row["TotalHours"]) if row and row["TotalHours"] is not None else 0.0

    def get_completed_events_count(self, user_id: int):
        """
        Count completed (past) events for a user.
        """
        sql = """
            SELECT COUNT(*) AS CompletedEvents
            FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
              AND TIMESTAMP(e.Date, e.StartTime) < NOW()
        """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return int(row["CompletedEvents"]) if row and row["CompletedEvents"] is not None else 0

    def get_badges(self, user_id: int):
        """
            Retrieve all badges earned by the user.
        """
        sql = """
            SELECT b.ID, b.Name, b.Description, b.IconURL
            FROM UserBadge ub
            JOIN Badge b ON b.ID = ub.BadgeID
            WHERE ub.UserID = %s
            ORDER BY b.Name ASC
        """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()