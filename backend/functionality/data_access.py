"""
This file includes all database interactions. 
"""
import bcrypt
from dotenv import load_dotenv
import os
import pymysql
import random
from pymysql.cursors import DictCursor
from flask import request
from datetime import date, timedelta

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
    # Badge Methods
    # ------------------------
    def get_user_badges(self, user_id: int):
        """
        Retrieve all badges earned by the user.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            List[Dict]: List of badge dictionaries
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

    def get_all_badges(self):
        """
        Retrieve all available badges in the system.
        
        Returns:
            List[Dict]: List of all badge dictionaries
        """
        sql = """
            SELECT ID, Name, Description, IconURL
            FROM Badge
            ORDER BY Name ASC
        """
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_badge_by_name(self, badge_name: str):
        """
        Retrieve a specific badge by its name.
        
        Args:
            badge_name (str): The name of the badge
            
        Returns:
            Dict: Badge dictionary or None if not found
        """
        sql = """
            SELECT ID, Name, Description, IconURL
            FROM Badge
            WHERE Name = %s
            LIMIT 1
        """
        with self.get_connection(use_dict_cursor=True) as conn, conn.cursor() as cursor:
            cursor.execute(sql, (badge_name,))
            return cursor.fetchone()

    def user_has_badge(self, user_id: int, badge_id: int) -> bool:
        """
        Check if a user has a specific badge.
        
        Args:
            user_id (int): The ID of the user
            badge_id (int): The ID of the badge
            
        Returns:
            bool: True if user has the badge, False otherwise
        """
        sql = """
            SELECT 1 FROM UserBadge
            WHERE UserID = %s AND BadgeID = %s
            LIMIT 1
        """
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id, badge_id))
            return cursor.fetchone() is not None

    def award_badge_to_user(self, user_id: int, badge_id: int):
        """
        Award a badge to a user.
        
        Args:
            user_id (int): The ID of the user
            badge_id (int): The ID of the badge to award
        """
        sql = """
            INSERT INTO UserBadge (UserID, BadgeID)
            VALUES (%s, %s)
        """
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id, badge_id))

    def user_completed_weekend_event(self, user_id: int) -> bool:
        """
        Check if a user has completed any events on weekends (Saturday or Sunday).
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            bool: True if user has completed a weekend event, False otherwise
        """
        sql = """
            SELECT 1 FROM Event e
            JOIN EventRegistration er ON er.EventID = e.ID
            WHERE er.UserID = %s
              AND TIMESTAMP(e.Date, e.StartTime) < NOW()
              AND DAYOFWEEK(e.Date) IN (1, 7)  -- Sunday=1, Saturday=7
            LIMIT 1
        """
        with self.get_connection() as conn, conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            return cursor.fetchone() is not None

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
            if not start_date and not end_date:
                start_date = date.today()
                # If we want to filter by default 30 days then uncomment below
                # end_date = start_date + timedelta(days=30)
            with self.get_connection(use_dict_cursor=True) as conn:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = """
                    SELECT e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.LocationPostcode, e.Capacity, e.Image_path,
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
                    GROUP BY e.ID, e.Title, e.About, e.Date, e.StartTime, e.EndTime, e.LocationCity, e.Address, e.LocationPostcode, e.Capacity, e.Image_path, c.Name
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
                            'LocationPostcode': item['LocationPostcode'],
                            'Capacity': item["Capacity"],
                            'Image_path': item['Image_path'],
                            'CauseName': item['CauseName'],
                            'TagName': item["TagName"]
                        })
        except pymysql.MySQLError as e:
            print(f"Database error in get_filtered_events: {e}")

        return events


    
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
        self.insert_user_in_team(owner_user_id, new_id)
        return self.get_team_by_id(new_id)

    def get_team_by_id(self, team_id: int):
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Team WHERE ID = %s", (team_id,))
            return cursor.fetchone()

    def get_team_by_join_code(self, join_code: str):
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM Team WHERE JoinCode = %s LIMIT 1", (join_code,))
            return cursor.fetchone()

    def list_all_teams(self, user_email):
        """
        Return ALL teams, newest first (ID DESC).
        """
        user_id = self.get_id_by_email(user_email)
        sql =  """
                SELECT ID, Name, Description, Department, Capacity, OwnerUserID, JoinCode, IsActive,
                CASE 
                WHEN OwnerUserID = %s THEN TRUE 
                ELSE FALSE 
                END AS IsOwner
                FROM Team
                ORDER BY ID DESC
                """
        with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, (user_id, ))
            return cursor.fetchall()


    # ------------------------
    # Team Logic Methods
    # ------------------------

    """Insert userID and teamID into TeamMembership table"""
    def insert_user_in_team(self, user_id, team_id):
        try:
            sql = "INSERT INTO TeamMembership (UserID, TeamID) VALUES (%s, %s)"
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(sql, (user_id, team_id))
        except Exception as e:
            print(f"Error in insert_user_in_team: {e}")
            raise

    """ Read team code using team ID """   
    def get_team_code(self, team_id):
        try:
            sql = "SELECT JoinCode FROM Team WHERE ID = %s"
            with self.get_connection() as conn, conn.cursor() as cursor:
                cursor.execute(sql, (team_id,))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Error in select_team_code: {e}")
            raise
    
    # """Delete userId and teamID from TeamMembership"""
    # def delete_user_from_team(self, user_email, team_id):
    #     user_id = self.get_id_by_email(user_email)
    #     try:
    #         sql = "DELETE FROM TeamMembership WHERE UserID = %s AND TeamID= %s"
    #         with self.get_connection() as conn, conn.cursor() as cursor:
    #             cursor.execute(sql, (user_id, team_id))
    #     except Exception as e:
    #         print(f"Error in delete_user_from_team: {e}")
    #         raise
    
    """Read all information on teams a user has joined"""
    def get_all_joined_teams(self, user_email):
        try:
            user_id = self.get_id_by_email(user_email)
            sql = """
                SELECT 
                    t.ID,
                    t.Name,
                    t.Description,
                    t.Department,
                    t.Capacity,
                    t.OwnerUserID,
                    t.JoinCode,
                    t.IsActive,
                    CASE 
                        WHEN t.OwnerUserID = %s THEN TRUE 
                        ELSE FALSE 
                    END AS IsOwner
                FROM Team AS t
                JOIN TeamMembership AS tm 
                    ON t.ID = tm.TeamID
                WHERE tm.UserID = %s
            """
            with self.get_connection() as conn, conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(sql, (user_id, user_id))
                result = cursor.fetchall()
                print("TEAMS IN DA")
                print(result)
                return result
        except Exception as e:
            print(f"Error in get_all_joined_teams: {e}")
            raise
