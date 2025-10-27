"""
This file includes all database interactions. 
"""
import bcrypt
from dotenv import load_dotenv
import os
import pymysql
import random
from pymysql.cursors import DictCursor

class DataAccess:
    load_dotenv()
    DB_HOST = os.getenv("MYSQL_HOST")
    DB_USER = os.getenv("MYSQL_USER")
    DB_DATABASE = os.getenv("MYSQL_DB")

    def __init__(self):
        load_dotenv()
        self.DB_HOST = os.getenv("MYSQL_HOST")
        self.DB_USER = os.getenv("MYSQL_USER")
        self.DB_DATABASE = os.getenv("MYSQL_DB")

    # conn = pymysql.connect(
    #     host=DB_HOST,
    #     user=DB_USER,
    #     database=DB_DATABASE
    # )


    def get_connection(self, use_dict_cursor=False):
        # Short-lived connections; no global shared conn.
        kwargs = {
            "host": self.DB_HOST,
            "user": self.DB_USER,
            "database": self.DB_DATABASE,
            "autocommit": True
        }
        if use_dict_cursor:
            kwargs["cursorclass"] = DictCursor

        return pymysql.connect(**kwargs)
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
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
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
    # Dashboard Methods
    # ------------------------
    def get_user_id_by_email(self, email):
        """
        Retrieve the unique user ID from the database using the user's email.
        """
        sql = "SELECT ID FROM User WHERE Email = %s LIMIT 1"
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
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
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id, int(limit)))
            return cursor.fetchall()
    
    def get_upcoming_events_paged(self, user_id: int, limit: int = 5, offset: int = 0):
        """
        Get upcoming events a user has registered for (future only) with pagination.
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
            LIMIT %s OFFSET %s
        """
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id, int(limit), int(offset)))
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
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
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
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return int(row["CompletedEvents"]) if row and row["CompletedEvents"] is not None else 0

    def get_completed_events(self, user_id: int, limit: int = 50):
        """
        Get completed (past) events a user has registered for.
        """
        sql = """
            SELECT 
                e.ID,
                e.Title,
                DATE_FORMAT(e.Date, '%%Y-%%m-%%d')      AS Date,
                DATE_FORMAT(e.StartTime, '%%H:%%i:%%s') AS StartTime,
                DATE_FORMAT(e.EndTime, '%%H:%%i:%%s')   AS EndTime,
                e.Address,
                e.LocationCity,
                e.LocationPostcode,
                TIME_TO_SEC(e.Duration) / 3600 AS DurationHours
            FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
              AND TIMESTAMP(e.Date, e.StartTime) < NOW()
            ORDER BY TIMESTAMP(e.Date, e.StartTime) DESC
            LIMIT %s
        """
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id, int(limit)))
            return cursor.fetchall()

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
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()

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
    # Events Search and Filter
    # ------------------------

    def get_location(self):
        location_list = []
        try:
            with self.get_connection(use_dict_cursor=True) as conn:
                with conn.cursor() as cursor:
                    query = "SELECT LocationCity FROM event"
                    cursor.execute(query)
                    result_set = cursor.fetchall()
                    location_list = sorted(set(row['LocationCity'] for row in result_set if row ['LocationCity']))
                    cursor.close()
        except pymysql.MySQLError as e:
            print(f"Database error in get_location: {e} ")
        return location_list
    

    # def get_all_events(self, location=None):
    #     event_list = []
    #     try:
    #         with self.get_connection(use_dict_cursor=True) as conn:
    #             with conn.cursor (pymysql.cursors.DictCursor) as cursor:
    #                 if location:
    #                     query = """
    #                     SELECT event.ID, event.Title, event.About, event.Date, event.StartTime, event.EndTime, event.LocationCity, event.Address, event.Capacity, Cause.Name as CauseName, GROUP_CONCAT(Tag.TagName SEPARATOR ',') AS TagName
    #                     FROM event e
    #                     JOIN Cause ON event.CauseID = Cause.ID
    #                     JOIN CauseTag ON Cause.ID = CauseTag.CauseID
    #                     JOIN Tag ON CauseTag.TagID = Tag.ID
    #                     WHERE ( %s IS NULL OR event.LocationCity = %s)
    #                     GROUP BY Event.ID
    #                     ORDER BY Event.Date ASC"""

    #                     cursor.execute(query, (location, location))

    #                     # cursor.execute(query, (location, location))
    #                 # else:
    #                 #     query = """
    #                 #     SELECT event.ID, event.Title, event.About, event.Date, event.StartTime, event.EndTime, event.LocationCity, event.Address, event.Capacity, Cause.Name as CauseName, GROUP_CONCAT(Tag.TagName SEPARATOR ',') AS TagName
    #                 #     FROM event 
    #                 #     JOIN Cause ON event.CauseID = Cause.ID
    #                 #     JOIN CauseTag ON Cause.ID = CauseTag.CauseID
    #                 #     JOIN Tag ON CauseTag.TagID = Tag.ID
    #                 #     GROUP BY Event.ID
    #                 #     ORDER BY Event.Date ASC"""
    #                     # cursor.execute(query)
    #                 result_set = cursor.fetchall()
        
    #                 for item in result_set:
    #                     event = {
    #                         'ID': item['ID'],
    #                         'Title': item["Title"],
    #                         'About': item["About"],
    #                         'Date': str(item["Date"]),
    #                         'StartTime': str(item["StartTime"]),
    #                         'EndTime': str(item["EndTime"]),
    #                         'LocationCity': item["LocationCity"],
    #                         'Address': item["Address"],
    #                         'Capacity': item["Capacity"],
    #                         'CauseName': item['CauseName'],
    #                         'TagName': item["TagName"]
    #                     }
    #                     event_list.append(event)
    #     except pymysql.MySQLError as e:
    #         print(f"Database error in get_all_events: {e}")
    
    #     return event_list

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
    # Events Search and Filter
    # ------------------------

    def get_location(self):
        location_list = []
        try:
            with self.get_connection(use_dict_cursor=True) as conn:
                with conn.cursor() as cursor:
                    query = "SELECT LocationCity FROM event"
                    cursor.execute(query)
                    result_set = cursor.fetchall()
                    location_list = sorted(set(row['LocationCity'] for row in result_set if row ['LocationCity']))
                    cursor.close()
        except pymysql.MySQLError as e:
            print(f"Database error in get_location: {e} ")
        return location_list
    

    def get_filtered_events(self, keyword=None, location=None, start_date=None, end_date=None):
        events = []
        try:
            with self.get_connection(use_dict_cursor=True) as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = """
                    SELECT e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity,
                        c.Name AS CauseName,
                        GROUP_CONCAT(t.TagName SEPARATOR ',') AS TagName
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
                        params.append(location.lower().strip())

                    if start_date and end_date:
                        query += " AND e.Date BETWEEN %s AND %s"
                        params.extend([start_date, end_date])
                    elif start_date:
                        query += " AND e.Date >= %s"
                        params.append(start_date)
                    elif end_date:
                        query += " AND e.Date <= %s"
                        params.append(end_date)

                    query += """
                    GROUP BY e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name
                    ORDER BY e.Date ASC;
                    """

                    cursor.execute(query, params)
                    result_set = cursor.fetchall()

                    
                    for item in result_set:
                        events.append({
                            'ID': item['ID'],
                            'Title': item["Title"],
                            'About': item["About"],
                            'Date': str(item["Date"]),
                            'StartTime': str(item["StartTime"]),
                            'EndTime': str(item["EndTime"]),
                            'LocationCity': item["LocationCity"],
                            'Address': item["Address"],
                            'Capacity': item["Capacity"],
                            'CauseName': item['CauseName'],
                            'TagName': item["TagName"]
                        })
        except pymysql.MySQLError as e:
            print(f"Database error in get_filtered_events: {e}")

        return events


    # def get_all_events(self, location=None):
    #     event_list = []
    #     try:
    #         with self.get_connection(use_dict_cursor=True) as conn:
    #             with conn.cursor(pymysql.cursors.DictCursor) as cursor:
    #                 query = """
    #                 SELECT e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName, GROUP_CONCAT(t.TagName SEPARATOR ',') AS TagName
    #                 FROM Event e
    #                 JOIN Cause c ON e.CauseID = c.ID
    #                 JOIN CauseTag ct ON c.ID = ct.CauseID
    #                 JOIN Tag t ON ct.TagID = t.ID
    #                 WHERE (%s IS NULL OR e.LocationCity = %s)
    #                 GROUP BY e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name
    #                 ORDER BY e.Date ASC;
    #                 """
    #                 loc_param = location.strip() if location else None
    #                 cursor.execute(query, (loc_param, loc_param))
    #                 result_set = cursor.fetchall()

    #                 for item in result_set:
    #                     event = {
    #                         'ID': item['ID'],
    #                         'Title': item["Title"],
    #                         'About': item["About"],
    #                         'Date': str(item["Date"]),
    #                         'StartTime': str(item["StartTime"]),
    #                         'EndTime': str(item["EndTime"]),
    #                         'LocationCity': item["LocationCity"],
    #                         'Address': item["Address"],
    #                         'Capacity': item["Capacity"],
    #                         'CauseName': item['CauseName'],
    #                         'TagName': item["TagName"]
    #                     }
    #                     event_list.append(event)
    #     except pymysql.MySQLError as e:
    #         print(f"Database error in get_all_events: {e}")

    #     return event_list


    # def search_events(self, keyword=None, location=None, date=None):
    #     events = []
    #     try:
    #         with self.get_connection(use_dict_cursor=True) as conn:
    #             cursor = conn.cursor()
    #             try:
    #                 query = """
                        
    #                 SELECT e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name AS CauseName, GROUP_CONCAT(t.TagName SEPARATOR ', ') AS TagNames
    #                 FROM Event e
    #                 JOIN Cause c ON e.CauseID = c.ID
    #                 JOIN CauseTag ct ON c.ID = ct.CauseID
    #                 JOIN Tag t ON ct.TagID = t.ID
    #                 WHERE 1=1
    #                 # GROUP BY e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.Capacity, c.Name;
    #                 """

    #                 params = []

    #                 if keyword:
    #                     query += " AND (e.Title LIKE %s OR e.About LIKE %s)"
    #                     keyword_param = f"%{keyword}%"
    #                     params.extend([keyword_param, keyword_param])

    #                 if location:
    #                     query += " AND LOWER(TRIM(e.LocationCity)) = %s"
    #                     params.append(location)

    #                 if date:
    #                     query += " AND e.Date = %s"
    #                     params.append(date)

    #                 query += " GROUP BY e.ID ORDER BY e.Date ASC"

    #                 print("Executing query with params:", query)

    #                 print("Executing query:", query)
    #                 print("Params:", params)

    #                 cursor.execute(query, params)
    #                 events = cursor.fetchall()

    #             finally:
    #                 cursor.close()
    #     except pymysql.MySQLError as e:
    #         print(f"Database error in search_events: {e}")
                   
    #     return events
    
    # -----------------------------
    # Teams: Data Access methods
    # -----------------------------
    def create_team(self, name, description, department, capacity, owner_user_id, join_code):
        """
        Insert a new team row and return the created team as a dict.
        """
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Team (Name, Description, Department, Capacity, OwnerUserID, JoinCode)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, description, department, capacity, owner_user_id, join_code),
            )
            new_id = cursor.lastrowid

        return self.get_team_by_id(new_id)

    def get_team_by_id(self, team_id: int):
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Team WHERE ID = %s", (team_id,))
            return cursor.fetchone()

    def get_team_by_join_code(self, join_code: str):
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Team WHERE JoinCode = %s LIMIT 1", (join_code,))
            return cursor.fetchone()

    def list_all_teams(self):
        """
        Return ALL teams, newest first (ID DESC).
        """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT ID, Name, Description, Department, Capacity, OwnerUserID, JoinCode, IsActive
                FROM Team
                ORDER BY ID DESC
                """
            )
            return cursor.fetchall()