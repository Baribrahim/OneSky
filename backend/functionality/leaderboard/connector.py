from typing import List, Dict, Any
from data_access import DataAccess

class LeaderboardConnector:
    """Handles leaderboard-related database operations."""
    
    def __init__(self, dao: DataAccess = None):
        self.dao = dao or DataAccess()

    def get_ordered_users(self, user_email) -> List[Dict[str, Any]]:
        """Gets users ordered by rank_score from DAO."""
        self.dao.update_rank_score(user_email)
        return self.dao.read_user_by_ordered_rank_score()

    def get_user_stats(self, user_email):
        return self.dao.read_user_stats(user_email)
    
    def get_user_current_rank(self, user_email):
        return self.dao.read_user_rank(user_email)