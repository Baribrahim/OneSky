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

    def reconnect(self):
        try:
            self.conn.ping(reconnect=True)
        except:
            self.conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                database=DB_DATABASE
    )

    print("Connected to database")

    # -----------------------------
    # Authentication Methods
    # -----------------------------
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

    """Gets all fields from event table"""    
    def get_event_details(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("select * from Event")
                return cursor.fetchall(), [col[0] for col in cursor.description]
        except Exception as e:
            print(f"Error in get_event_details: {e}")
            raise

    """Gets the users id by querying the table by email"""
    def get_id_by_email(self, email):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT ID FROM User WHERE Email = %s", (email,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error in get_id_by_email: {e}")
            raise

    """Stores the user id and corresponding event id in database"""
    def store_user_event_id(self, user_email, event_id):
        try:
            user_id = self.get_id_by_email(user_email)
            with self.conn.cursor() as cursor:
                cursor.execute("INSERT INTO EventRegistration (UserID, EventID) VALUES (%s, %s)", (user_id, event_id))
                self.conn.commit()
        except Exception as e:
            print(f"Error in store_user_event_id: {e}")
            raise

    """Get all events a user is signed up for"""
    def get_user_events(self, user_email):
        try:
            user_id = self.get_id_by_email(user_email)
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT EventID FROM EventRegistration WHERE UserID = %s", (user_id))
                result = cursor.fetchall()
                return result
        except Exception as e:
            print(f"Error in check_user_event_signup: {e}")
            raise
    
    """Removes userId and eventId from EventRegistration table"""
    def delete_user_from_event(self, user_email, event_id):
        try:
            user_id = self.get_id_by_email(user_email)
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM EventRegistration WHERE UserID = %s AND EventID = %s", (user_id, event_id))
                self.conn.commit()
        except Exception as e:
            print(f"Error in unregister_user_from_event: {e}")
            raise    

    # -----------------------------
    # Dashboard Methods
    # -----------------------------
    def get_user_id_by_email(self, email):
        """
        Retrieve the unique user ID from the database using the user's email.

        SQL Logic:
        - Selects the ID column from the User table where the Email matches the input.
        - LIMIT 1 ensures only one result is returned (since email should be unique).

        Args:
            email (str): The user's email address.
        Returns:
            int | None: The user's ID if found, otherwise None.
        """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT ID FROM User WHERE Email = %s LIMIT 1", (email,))
            row = cursor.fetchone()
            return row["ID"] if row else None
    

    def get_upcoming_events(self, user_id: int, limit: int = 5):
        """
        Get all upcoming events that a user has registered for.

        SQL Logic:
        - Joins Event and EventRegistration tables to find events the user is signed up for.
        - Filters only future events (TIMESTAMP(e.Date, e.StartTime) > NOW()).
        - Returns readable date and time strings for frontend use.
        """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
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
            """, (user_id, int(limit)))
            return cursor.fetchall()
  

    def get_total_hours(self, user_id: int):
        """
        Calculate the total number of hours a user has *completed* from past events.

        SQL Logic:
        - Sums up the Duration (stored as TIME) of all events linked to the user.
        - Converts TIME values to seconds, then divides by 3600 to get hours.
        - Includes only past events (event start time < NOW()).
        - Uses COALESCE to return 0 if there are no results.

        Args:
            user_id (int): The ID of the user.
        Returns:
            float: The total completed hours (e.g., 12.5 hours).
        """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(TIME_TO_SEC(e.Duration)) / 3600, 0) AS TotalHours
                FROM Event e
                JOIN EventRegistration er ON er.EventID = e.ID
                WHERE er.UserID = %s
                  AND TIMESTAMP(e.Date, e.StartTime) < NOW()
            """, (user_id,))
            row = cursor.fetchone()
            return float(row["TotalHours"]) if row and row["TotalHours"] is not None else 0.0


    def get_completed_events_count(self, user_id: int):
        """
        Get the total number of completed events for a given user.

        SQL Logic:
        - Selects all events joined with EventRegistration for this user.
        - Counts events that are already finished (start time < NOW()).
        - Returns the total count of completed events.

        Args:
            user_id (int): The ID of the user.

        Returns:
            int: Number of completed events.
        """
        query = """
            SELECT COUNT(*) AS CompletedEvents
            FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
            AND TIMESTAMP(e.Date, e.StartTime) < NOW()
        """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return int(result["CompletedEvents"]) if result and result["CompletedEvents"] is not None else 0



    def get_badges(self, user_id: int):
        """
        Retrieve all badges earned by the user.

        SQL Logic:
        - Joins UserBadge and Badge tables to get badge info linked to the user.
        - Orders results alphabetically by badge name.

        Args:
            user_id (int): The ID of the user.
        Returns:
            list[dict]: A list of badges with ID, Name, Description, and IconURL.
        """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("""
                SELECT b.ID, b.Name, b.Description, b.IconURL
                FROM UserBadge ub
                JOIN Badge b ON b.ID = ub.BadgeID
                WHERE ub.UserID = %s
                ORDER BY b.Name ASC
            """, (user_id,)) 
            return cursor.fetchall()

    # -----------------------------
    # Teams: Data Access methods
    # -----------------------------
    def create_team(self, name, description, department, capacity, owner_user_id, join_code):
        """
        Insert a new team row and return the created team as a dict.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Team (Name, Description, Department, Capacity, OwnerUserID, JoinCode)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, description, department, capacity, owner_user_id, join_code),
            )
            self.conn.commit()
            new_id = cursor.lastrowid

        return self.get_team_by_id(new_id)

    def get_team_by_id(self, team_id: int):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Team WHERE ID = %s", (team_id,))
            return cursor.fetchone()

    def get_team_by_join_code(self, join_code: str):
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Team WHERE JoinCode = %s LIMIT 1", (join_code,))
            return cursor.fetchone()

    def list_all_teams(self):
        """
        Return ALL teams, newest first (ID DESC).
        """
        with self.conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT ID, Name, Description, Department, Capacity, OwnerUserID, JoinCode, IsActive
                FROM Team
                ORDER BY ID DESC
                """
            )
            return cursor.fetchall()