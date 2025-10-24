"""
Badge Connector - Middle layer between routes and data access for badge functionality.
Handles business logic for badge operations including earning, checking, and retrieving badges.
"""

from data_access import DataAccess
from typing import List, Dict, Optional, Tuple


class BadgeConnector:
    """
    Middle layer connector for badge operations.
    Handles business logic and validation for badge-related operations.
    """
    
    def __init__(self):
        """Initialize the connector with data access layer."""
        self.data_access = DataAccess()
    
    def get_user_badges(self, user_id: int) -> List[Dict]:
        """
        Retrieve all badges earned by a specific user.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            List[Dict]: List of badge dictionaries with ID, Name, Description, IconURL
        """
        try:
            badges = self.data_access.get_user_badges(user_id)
            return badges if badges else []
        except Exception as e:
            print(f"BadgeConnector: Error retrieving user badges - {e}")
            return []
    
    def get_all_badges(self) -> List[Dict]:
        """
        Retrieve all available badges in the system.
        
        Returns:
            List[Dict]: List of all badge dictionaries
        """
        try:
            badges = self.data_access.get_all_badges()
            return badges if badges else []
        except Exception as e:
            print(f"BadgeConnector: Error retrieving all badges - {e}")
            return []
    
    def award_badge_to_user(self, user_id: int, badge_id: int) -> Tuple[bool, str]:
        """
        Award a specific badge to a user.
        
        Args:
            user_id (int): The ID of the user
            badge_id (int): The ID of the badge to award
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Check if user already has this badge
            if self.data_access.user_has_badge(user_id, badge_id):
                return False, "User already has this badge"
            
            # Award the badge
            self.data_access.award_badge_to_user(user_id, badge_id)
            return True, "Badge awarded successfully"
            
        except Exception as e:
            print(f"BadgeConnector: Error awarding badge - {e}")
            return False, f"Error awarding badge: {str(e)}"
    
    def check_and_award_event_badges(self, user_id: int) -> List[Dict]:
        """
        Check user's event participation and award appropriate badges.
        This is the main method for automatic badge awarding based on user activity.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            List[Dict]: List of newly awarded badges
        """
        newly_awarded = []
        
        try:
            # Get user statistics
            upcoming_count = self.data_access.get_upcoming_events_count(user_id)
            completed_count = self.data_access.get_completed_events_count(user_id)
            total_hours = self.data_access.get_total_hours(user_id)
            
            # Check for Event Starter badge (1 upcoming event)
            if upcoming_count >= 1:
                event_starter_badge = self.data_access.get_badge_by_name("Event Starter")
                if event_starter_badge and not self.data_access.user_has_badge(user_id, event_starter_badge["ID"]):
                    success, _ = self.award_badge_to_user(user_id, event_starter_badge["ID"])
                    if success:
                        newly_awarded.append(event_starter_badge)
            
            # Check for Event Enthusiast badge (5 upcoming events)
            if upcoming_count >= 5:
                event_enthusiast_badge = self.data_access.get_badge_by_name("Event Enthusiast")
                if event_enthusiast_badge and not self.data_access.user_has_badge(user_id, event_enthusiast_badge["ID"]):
                    success, _ = self.award_badge_to_user(user_id, event_enthusiast_badge["ID"])
                    if success:
                        newly_awarded.append(event_enthusiast_badge)
            
            # Check for First Step badge (1 completed event)
            if completed_count >= 1:
                first_step_badge = self.data_access.get_badge_by_name("First Step")
                if first_step_badge and not self.data_access.user_has_badge(user_id, first_step_badge["ID"]):
                    success, _ = self.award_badge_to_user(user_id, first_step_badge["ID"])
                    if success:
                        newly_awarded.append(first_step_badge)
            
            # Check for Volunteer Veteran badge (10 completed events)
            if completed_count >= 10:
                volunteer_veteran_badge = self.data_access.get_badge_by_name("Volunteer Veteran")
                if volunteer_veteran_badge and not self.data_access.user_has_badge(user_id, volunteer_veteran_badge["ID"]):
                    success, _ = self.award_badge_to_user(user_id, volunteer_veteran_badge["ID"])
                    if success:
                        newly_awarded.append(volunteer_veteran_badge)
            
            # Check for Marathon Helper badge (20+ hours)
            if total_hours >= 20:
                marathon_helper_badge = self.data_access.get_badge_by_name("Marathon Helper")
                if marathon_helper_badge and not self.data_access.user_has_badge(user_id, marathon_helper_badge["ID"]):
                    success, _ = self.award_badge_to_user(user_id, marathon_helper_badge["ID"])
                    if success:
                        newly_awarded.append(marathon_helper_badge)
            
            # Check for Weekend Warrior badge (completed weekend event)
            if self.data_access.user_completed_weekend_event(user_id):
                weekend_warrior_badge = self.data_access.get_badge_by_name("Weekend Warrior")
                if weekend_warrior_badge and not self.data_access.user_has_badge(user_id, weekend_warrior_badge["ID"]):
                    success, _ = self.award_badge_to_user(user_id, weekend_warrior_badge["ID"])
                    if success:
                        newly_awarded.append(weekend_warrior_badge)
            
        except Exception as e:
            print(f"BadgeConnector: Error checking and awarding badges - {e}")
        
        return newly_awarded
    
    def get_user_badge_progress(self, user_id: int) -> Dict:
        """
        Get user's progress towards earning badges.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            Dict: Progress information for badge earning
        """
        try:
            upcoming_count = self.data_access.get_upcoming_events_count(user_id)
            completed_count = self.data_access.get_completed_events_count(user_id)
            total_hours = self.data_access.get_total_hours(user_id)
            has_weekend_event = self.data_access.user_completed_weekend_event(user_id)
            
            return {
                "upcoming_events": upcoming_count,
                "completed_events": completed_count,
                "total_hours": total_hours,
                "has_weekend_event": has_weekend_event,
                "badge_progress": {
                    "event_starter": {"required": 1, "current": upcoming_count, "earned": upcoming_count >= 1},
                    "event_enthusiast": {"required": 5, "current": upcoming_count, "earned": upcoming_count >= 5},
                    "first_step": {"required": 1, "current": completed_count, "earned": completed_count >= 1},
                    "volunteer_veteran": {"required": 10, "current": completed_count, "earned": completed_count >= 10},
                    "marathon_helper": {"required": 20, "current": total_hours, "earned": total_hours >= 20},
                    "weekend_warrior": {"required": 1, "current": 1 if has_weekend_event else 0, "earned": has_weekend_event}
                }
            }
        except Exception as e:
            print(f"BadgeConnector: Error getting badge progress - {e}")
            return {}

