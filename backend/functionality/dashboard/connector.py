# dashboard/connector.py
from typing import Dict, Any, List
from data_access import DataAccess

class DashboardConnector:
    def __init__(self):
        self.da = DataAccess()

    def _get_user_id_or_raise(self, email: str) -> int:
        if not email or "@" not in email:
            raise ValueError("Invalid user identity")
        user_id = self.da.get_user_id_by_email(email)
        if not user_id:
            raise ValueError("User not found")
        return user_id

    def get_upcoming_events(self, email: str, limit: int = 5) -> List[dict]:
        user_id = self._get_user_id_or_raise(email)
        limit = max(1, min(int(limit or 5), 25))
        return self.da.get_upcoming_events(user_id, limit)

    def get_total_hours(self, email: str) -> float:
        user_id = self._get_user_id_or_raise(email)
        return self.da.get_total_hours(user_id)

    def get_badges(self, email: str) -> List[dict]:
        user_id = self._get_user_id_or_raise(email)
        return self.da.get_badges(user_id)

    def get_dashboard(self, email: str, limit: int = 5) -> Dict[str, Any]:
        return {
            "upcoming_events": self.get_upcoming_events(email, limit),
            "total_hours": self.get_total_hours(email),
            "badges": self.get_badges(email),
        }
