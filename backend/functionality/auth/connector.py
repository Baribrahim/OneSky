import bcrypt       
from data_access import DataAccess

""" Middle layer between routes and data access """
class Connector():


    """Authentication Methods that uses DataAccess methods"""
    def add_user(self, email, password, FirstName, LastName):
        da = DataAccess()

        # Validation: check if user already exists
        if da.user_exists(email):
            print("CONNECTOR: User already exists")
            return False, "User already exists"

        # Validation: password length
        if len(password) < 8:
            print("CONNECTOR: Password too short")
            return False, "Password must be at least 8 characters"

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