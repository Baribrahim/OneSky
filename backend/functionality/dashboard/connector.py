# dashboard/connector.py
from typing import Dict, Any, List
from data_access import DataAccess

class DashboardConnector:
    def __init__(self):
        self.da = DataAccess()

    def get_user_id(self, email: str) -> int:
        if not email or "@" not in email:
            raise ValueError("Invalid user identity")
        user_id = self.da.get_user_id_by_email(email)
        if not user_id:
            raise ValueError("User not found")
        return user_id

    def get_upcoming_events(self, email: str, limit: int = 5) -> List[dict]:
        user_id = self.get_user_id(email)
        limit = max(1, min(int(limit or 5), 25))
        return self.da.get_upcoming_events(user_id, limit)
    
    def get_upcoming_events_paged(self, email: str, limit: int = 5, offset: int = 0) -> List[dict]:
        user_id = self.get_user_id(email)
        limit = max(1, min(int(limit or 5), 50))  # you can raise cap if you want
        offset = max(0, int(offset or 0))
        return self.da.get_upcoming_events_paged(user_id, limit, offset)

    def get_upcoming_events_count(self, email: str) -> int:
        user_id = self.get_user_id(email)
        return self.da.get_upcoming_events_count(user_id)

    def get_total_hours(self, email: str) -> float:
        user_id = self.get_user_id(email)
        return self.da.get_total_hours(user_id)

    def get_completed_events_count(self, email: str) -> int:
        user_id = self.get_user_id(email)
        return self.da.get_completed_events_count(user_id)

    def get_completed_events(self, email: str, limit: int = 50) -> List[dict]:
        user_id = self.get_user_id(email)
        limit = max(1, min(int(limit or 50), 100))  # reasonable cap
        return self.da.get_completed_events(user_id, limit)

    def get_badges(self, email: str) -> List[dict]:
        user_id = self.get_user_id(email)
        return self.da.get_badges(user_id)

    def get_dashboard(self, email: str, limit: int = 5) -> Dict[str, Any]:
        """Aggregate all dashboard data into one structure"""
        user_id = self.get_user_id(email)
        return {
            "upcoming_events": self.da.get_upcoming_events(user_id, limit),
            "upcoming_count": self.da.get_upcoming_events_count(user_id),
            "total_hours": self.da.get_total_hours(user_id),
            "completed_events": self.da.get_completed_events_count(user_id),
            "badges": self.da.get_badges(user_id),
        }