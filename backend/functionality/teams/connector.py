import random
import string
from typing import Dict, Any, List
from data_access import DataAccess

ALPHABET = string.ascii_uppercase + string.digits

def generate_join_code(length: int = 8) -> str:
    """Return an upper-case alphanumeric code of given length."""
    return "".join(random.choice(ALPHABET) for _ in range(length))

class TeamConnector:
    """
    Teams business logic layer.
    - Validates inputs
    - Resolves owner by email
    - Generates unique JoinCode (retries on collision)
    """
    
    def __init__(self, da: DataAccess | None = None):
        self.da = da or DataAccess()

    # ---------- helpers ----------
    @staticmethod
    def validate_team_input(name: str, description, department, capacity):
        if not name or not name.strip():
            raise ValueError("Name is required.")
        if len(name) > 120:
            raise ValueError("Name must be at most 120 characters.")
        if capacity is not None:
            try:
                cap = int(capacity)
            except (TypeError, ValueError):
                raise ValueError("Capacity must be a positive integer.")
            if cap < 1:
                raise ValueError("Capacity must be >= 1.")

    def owner_id_from_email(self, email: str) -> int:
        owner_id = self.da.get_user_id_by_email(email)
        if not owner_id:
            raise ValueError("User not found.")
        return int(owner_id)

    def unique_join_code(self) -> str:
        for _ in range(10):
            code = generate_join_code(8)
            if not self.da.get_team_by_join_code(code):
                return code
        raise RuntimeError("Could not generate a unique join code; please retry.")
    # -----------------------------

    def create_team(self, creator_email: str, name: str, description, department, capacity) -> Dict[str, Any]:
        self.validate_team_input(name, description, department, capacity)
        owner_id = self.owner_id_from_email(creator_email)
        code = self.unique_join_code()
        return self.da.create_team(name.strip(), description, department, capacity, owner_id, code)

    def browse_all_teams(self) -> List[Dict[str, Any]]:
        return self.da.list_all_teams()

    """Passes users email and team id to dao"""
    def add_user_to_team(self, user_email, team_id):
        self.da.insert_user_in_team(user_email, team_id)

    """Pass user input code to dao for verification"""
    def verify_team_code(self, team_id, join_code):
        actual_code = self.da.get_team_code(team_id)
        return actual_code == join_code
    
    # """ Passes teams user has joined"""
    # def user_joined_teams(self, user_email):
    #     dao = DataAccess()
    #     data_tuple_of_tuple = dao.get_all_joined_teams(user_email)
    #     all_teams = [x[0] for x in data_tuple_of_tuple]
    #     return all_teams