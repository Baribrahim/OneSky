"""
Test suite for badge functionality using pytest.
Tests cover BadgeConnector, DataAccess badge methods, and badge routes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from badges.connector import BadgeConnector
from data_access import DataAccess


class TestBadgeConnector:
    """Test cases for BadgeConnector class."""
    
    @pytest.fixture
    def connector(self):
        """Set up test fixtures before each test method."""
        connector = BadgeConnector()
        mock_data_access = Mock()
        connector.data_access = mock_data_access
        return connector
    
    def test_get_user_badges_success(self, connector):
        """Test successful retrieval of user badges."""
        # Arrange
        user_id = 1
        expected_badges = [
            {"ID": 1, "Name": "Event Starter", "Description": "Registered for 1 upcoming events.", "IconURL": "/src/assets/badges/firstStep.png"},
            {"ID": 2, "Name": "First Step", "Description": "Completed your first volunteering event.", "IconURL": "/src/assets/badges/firstStep.png"}
        ]
        connector.data_access.get_user_badges.return_value = expected_badges
        
        # Act
        result = connector.get_user_badges(user_id)
        
        # Assert
        assert result == expected_badges
        connector.data_access.get_user_badges.assert_called_once_with(user_id)
    
    def test_get_user_badges_empty(self, connector):
        """Test retrieval of user badges when user has no badges."""
        # Arrange
        user_id = 1
        connector.data_access.get_user_badges.return_value = []
        
        # Act
        result = connector.get_user_badges(user_id)
        
        # Assert
        assert result == []
    
    def test_get_user_badges_exception(self, connector):
        """Test handling of exceptions in get_user_badges."""
        # Arrange
        user_id = 1
        connector.data_access.get_user_badges.side_effect = Exception("Database error")
        
        # Act
        result = connector.get_user_badges(user_id)
        
        # Assert
        assert result == []
    
    def test_get_all_badges_success(self, connector):
        """Test successful retrieval of all badges."""
        # Arrange
        expected_badges = [
            {"ID": 1, "Name": "Event Starter", "Description": "Registered for 1 upcoming events.", "IconURL": "/src/assets/badges/firstStep.png"},
            {"ID": 2, "Name": "Event Enthusiast", "Description": "Registered for 5 upcoming events.", "IconURL": "/src/assets/badges/eduEnthusiast.png"},
            {"ID": 3, "Name": "First Step", "Description": "Completed your first volunteering event.", "IconURL": "/src/assets/badges/firstStep.png"}
        ]
        connector.data_access.get_all_badges.return_value = expected_badges
        
        # Act
        result = connector.get_all_badges()
        
        # Assert
        assert result == expected_badges
        connector.data_access.get_all_badges.assert_called_once()
    
    def test_award_badge_to_user_success(self, connector):
        """Test successful badge awarding."""
        # Arrange
        user_id = 1
        badge_id = 2
        connector.data_access.user_has_badge.return_value = False
        
        # Act
        success, message = connector.award_badge_to_user(user_id, badge_id)
        
        # Assert
        assert success is True
        assert message == "Badge awarded successfully"
        connector.data_access.user_has_badge.assert_called_once_with(user_id, badge_id)
        connector.data_access.award_badge_to_user.assert_called_once_with(user_id, badge_id)
    
    def test_award_badge_to_user_already_has(self, connector):
        """Test badge awarding when user already has the badge."""
        # Arrange
        user_id = 1
        badge_id = 2
        connector.data_access.user_has_badge.return_value = True
        
        # Act
        success, message = connector.award_badge_to_user(user_id, badge_id)
        
        # Assert
        assert success is False
        assert message == "User already has this badge"
        connector.data_access.user_has_badge.assert_called_once_with(user_id, badge_id)
        connector.data_access.award_badge_to_user.assert_not_called()
    
    def test_award_badge_to_user_exception(self, connector):
        """Test handling of exceptions in award_badge_to_user."""
        # Arrange
        user_id = 1
        badge_id = 2
        connector.data_access.user_has_badge.side_effect = Exception("Database error")
        
        # Act
        success, message = connector.award_badge_to_user(user_id, badge_id)
        
        # Assert
        assert success is False
        assert "Error awarding badge" in message
    
    def test_check_and_award_event_badges_event_starter(self, connector):
        """Test awarding Event Starter badge."""
        # Arrange
        user_id = 1
        connector.data_access.get_upcoming_events_count.return_value = 1
        connector.data_access.get_completed_events_count.return_value = 0
        connector.data_access.get_total_hours.return_value = 0.0
        connector.data_access.user_completed_weekend_event.return_value = False
        
        event_starter_badge = {"ID": 1, "Name": "Event Starter", "Description": "Registered for 1 upcoming events.", "IconURL": "/src/assets/badges/firstStep.png"}
        connector.data_access.get_badge_by_name.return_value = event_starter_badge
        connector.data_access.user_has_badge.return_value = False
        
        # Act
        result = connector.check_and_award_event_badges(user_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["Name"] == "Event Starter"
    
    def test_check_and_award_event_badges_first_step(self, connector):
        """Test awarding First Step badge."""
        # Arrange
        user_id = 1
        connector.data_access.get_upcoming_events_count.return_value = 0
        connector.data_access.get_completed_events_count.return_value = 1
        connector.data_access.get_total_hours.return_value = 0.0
        connector.data_access.user_completed_weekend_event.return_value = False
        
        first_step_badge = {"ID": 3, "Name": "First Step", "Description": "Completed your first volunteering event.", "IconURL": "/src/assets/badges/firstStep.png"}
        connector.data_access.get_badge_by_name.return_value = first_step_badge
        connector.data_access.user_has_badge.return_value = False
        
        # Act
        result = connector.check_and_award_event_badges(user_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["Name"] == "First Step"
    
    def test_check_and_award_event_badges_marathon_helper(self, connector):
        """Test awarding Marathon Helper badge."""
        # Arrange
        user_id = 1
        connector.data_access.get_upcoming_events_count.return_value = 0
        connector.data_access.get_completed_events_count.return_value = 0
        connector.data_access.get_total_hours.return_value = 25.0
        connector.data_access.user_completed_weekend_event.return_value = False
        
        marathon_helper_badge = {"ID": 5, "Name": "Marathon Helper", "Description": "Contributed 20+ total volunteering hours.", "IconURL": "/src/assets/badges/marathonVolunteer.png"}
        connector.data_access.get_badge_by_name.return_value = marathon_helper_badge
        connector.data_access.user_has_badge.return_value = False
        
        # Act
        result = connector.check_and_award_event_badges(user_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["Name"] == "Marathon Helper"
    
    def test_check_and_award_event_badges_weekend_warrior(self, connector):
        """Test awarding Weekend Warrior badge."""
        # Arrange
        user_id = 1
        connector.data_access.get_upcoming_events_count.return_value = 0
        connector.data_access.get_completed_events_count.return_value = 0
        connector.data_access.get_total_hours.return_value = 0.0
        connector.data_access.user_completed_weekend_event.return_value = True
        
        weekend_warrior_badge = {"ID": 6, "Name": "Weekend Warrior", "Description": "Completed an event on a Saturday or Sunday.", "IconURL": "/src/assets/badges/weekendWarrior.png"}
        connector.data_access.get_badge_by_name.return_value = weekend_warrior_badge
        connector.data_access.user_has_badge.return_value = False
        
        # Act
        result = connector.check_and_award_event_badges(user_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["Name"] == "Weekend Warrior"
    
    def test_get_user_badge_progress(self, connector):
        """Test getting user badge progress."""
        # Arrange
        user_id = 1
        connector.data_access.get_upcoming_events_count.return_value = 3
        connector.data_access.get_completed_events_count.return_value = 2
        connector.data_access.get_total_hours.return_value = 15.0
        connector.data_access.user_completed_weekend_event.return_value = True
        
        # Act
        result = connector.get_user_badge_progress(user_id)
        
        # Assert
        assert result["upcoming_events"] == 3
        assert result["completed_events"] == 2
        assert result["total_hours"] == 15.0
        assert result["has_weekend_event"] is True
        
        # Check badge progress
        progress = result["badge_progress"]
        assert progress["event_starter"]["earned"] is True  # 3 >= 1
        assert progress["event_enthusiast"]["earned"] is False  # 3 < 5
        assert progress["first_step"]["earned"] is True  # 2 >= 1
        assert progress["volunteer_veteran"]["earned"] is False  # 2 < 10
        assert progress["marathon_helper"]["earned"] is False  # 15 < 20
        assert progress["weekend_warrior"]["earned"] is True  # has weekend event


class TestDataAccessBadgeMethods:
    """Test cases for DataAccess badge methods using a context-manager mock for pymysql.connect."""

    @pytest.fixture
    def data_access(self):
        return DataAccess()

    def _setup_cm_mocks(self, mock_connect):
        """Helper to set up connection and cursor context manager behaviour."""
        mock_conn = MagicMock(name="conn")
        mock_cursor = MagicMock(name="cursor")

        # pymysql.connect() returns a connection that is used as a context manager
        mock_connect.return_value.__enter__.return_value = mock_conn
        # conn.cursor() returns a cursor that is used as a context manager
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        return mock_conn, mock_cursor

    @patch('data_access.pymysql.connect')
    def test_get_user_badges(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)

        expected_badges = [
            {"ID": 1, "Name": "Event Starter", "Description": "Registered for 1 upcoming events.", "IconURL": "/src/assets/badges/firstStep.png"}
        ]
        mock_cursor.fetchall.return_value = expected_badges

        result = data_access.get_user_badges(1)

        assert result == expected_badges
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @patch('data_access.pymysql.connect')
    def test_get_all_badges(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)

        expected_badges = [
            {"ID": 1, "Name": "Event Starter", "Description": "Registered for 1 upcoming events.", "IconURL": "/src/assets/badges/firstStep.png"},
            {"ID": 2, "Name": "Event Enthusiast", "Description": "Registered for 5 upcoming events.", "IconURL": "/src/assets/badges/eduEnthusiast.png"}
        ]
        mock_cursor.fetchall.return_value = expected_badges

        result = data_access.get_all_badges()

        assert result == expected_badges
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @patch('data_access.pymysql.connect')
    def test_get_badge_by_name(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)

        expected_badge = {
            "ID": 1, "Name": "Event Starter", "Description": "Registered for 1 upcoming events.", "IconURL": "/src/assets/badges/firstStep.png"
        }
        mock_cursor.fetchone.return_value = expected_badge

        result = data_access.get_badge_by_name("Event Starter")

        assert result == expected_badge
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @patch('data_access.pymysql.connect')
    def test_user_has_badge_true(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)
        mock_cursor.fetchone.return_value = (1,)  # count > 0

        result = data_access.user_has_badge(1, 2)

        assert result is True
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @patch('data_access.pymysql.connect')
    def test_user_has_badge_false(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)
        mock_cursor.fetchone.return_value = None  # no row

        result = data_access.user_has_badge(1, 2)

        assert result is False
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @patch('data_access.pymysql.connect')
    def test_award_badge_to_user(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)

        data_access.award_badge_to_user(1, 2)

        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        assert mock_cursor.execute.called, "Expected an INSERT/UPDATE execute call"

    @patch('data_access.pymysql.connect')
    def test_user_completed_weekend_event_true(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)
        mock_cursor.fetchone.return_value = (1,)  # at least one weekend event

        result = data_access.user_completed_weekend_event(1)

        assert result is True
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()

    @patch('data_access.pymysql.connect')
    def test_user_completed_weekend_event_false(self, mock_connect, data_access):
        mock_conn, mock_cursor = self._setup_cm_mocks(mock_connect)
        mock_cursor.fetchone.return_value = None  # none found

        result = data_access.user_completed_weekend_event(1)

        assert result is False
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()



# # Pytest configuration and test discovery
# if __name__ == '__main__':
#     pytest.main([__file__, '-v'])