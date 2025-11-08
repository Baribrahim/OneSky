import bcrypt       
import re
from data_access import DataAccess

""" Middle layer between routes and data access """
class Connector():


    """Authentication Methods that uses DataAccess methods"""
    def add_user(self, email, password, FirstName, LastName):
        da = DataAccess()

        # Validation: check required fields
        if not email:
            print("CONNECTOR: Email is required")
            return False, "Email is required"
        
        if not password:
            print("CONNECTOR: Password is required")
            return False, "Password is required"

        # Validation: check if user already exists
        if da.user_exists(email):
            print("CONNECTOR: User already exists")
            return False, "User already exists"

        # Validation: email domain (Sky internal only)
        email_pattern = re.compile(r"^[A-Za-z0-9._%+-]+@sky\.uk$")
        if not email_pattern.match(email):
            print("CONNECTOR: Invalid email domain")
            return False, "Email address not in a valid format"

        # Validation: password strength
        # At least 8 chars, one uppercase, one number, one special char
        password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$")
        if not password_pattern.match(password):
            print("CONNECTOR: Weak password")
            return False, "Password must be at least 8 characters and include an uppercase letter, a number, and a special character."

        # Hash password and insert
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        da.create_user(email, hashed_password, FirstName, LastName)

        return True, "User created successfully"
    
    def verify_user_by_password(self, email, password):
        da = DataAccess()
        return da.verify_user_by_password(email, password)
    
    def get_user_id_by_email(self, email):
        da = DataAccess()
        return da.get_user_id_by_email(email)