from typing import List, Dict, Any
from data_access import DataAccess
import bcrypt

class ProfileConnector:
    """Handles profile-related database operations."""
    
    def __init__(self, dao: DataAccess = None):
        self.dao = dao or DataAccess()

    def get_user_details(self, user_email):
        """Gets users info from DAO."""
        return self.dao.read_user_info(user_email)
    
    def update_profile_image(self, user_email: str, image_path: str) -> bool:
        """
        Updates the user's profile image.

        :param user_email: str - email of the user
        :param image_path: str - new profile image path
        :return: bool - True if update succeeded, False otherwise
        """
        return self.dao.update_profile_image(user_email, image_path)
    
    def update_user_password(self, user_email, old_password, new_password):
        """Hashed and updates the user's password."""
        if self.dao.verify_user_by_password(user_email, old_password) is None:
                return False
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        self.dao.update_user_password(user_email, hashed_password)
        return True