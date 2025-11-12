"""
Test suite for DashboardConnector using pytest.
Tests cover all DashboardConnector methods with mocked data access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.connector import DashboardConnector
from data_access import DataAccess


@pytest.fixture
def mock_data_access():
    """Fixture for mocked DataAccess."""
    return Mock(spec=DataAccess)


@pytest.fixture
def connector(mock_data_access):
    """Fixture for DashboardConnector with mocked data access."""
    connector = DashboardConnector()
    connector.da = mock_data_access
    return connector


def test_get_user_id_success(connector, mock_data_access):
    """Test successful user ID retrieval."""
    mock_data_access.get_user_id_by_email.return_value = 1
    
    result = connector.get_user_id("test@example.com")
    
    assert result == 1
    mock_data_access.get_user_id_by_email.assert_called_once_with("test@example.com")


def test_get_user_id_invalid_email(connector):
    """Test get_user_id with invalid email."""
    with pytest.raises(ValueError, match="Invalid user identity"):
        connector.get_user_id("invalid-email")


def test_get_user_id_empty_email(connector):
    """Test get_user_id with empty email."""
    with pytest.raises(ValueError, match="Invalid user identity"):
        connector.get_user_id("")


def test_get_user_id_not_found(connector, mock_data_access):
    """Test get_user_id when user is not found."""
    mock_data_access.get_user_id_by_email.return_value = None
    
    with pytest.raises(ValueError, match="User not found"):
        connector.get_user_id("nonexistent@example.com")


def test_get_upcoming_events_success(connector, mock_data_access):
    """Test successful retrieval of upcoming events."""
    mock_data_access.get_user_id_by_email.return_value = 1
    expected_events = [{"ID": 1, "Title": "Event 1"}]
    mock_data_access.get_upcoming_events.return_value = expected_events
    
    result = connector.get_upcoming_events("test@example.com", limit=5)
    
    assert result == expected_events
    mock_data_access.get_upcoming_events.assert_called_once_with(1, 5)


def test_get_upcoming_events_limit_clamping(connector, mock_data_access):
    """Test that limit is properly clamped."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_upcoming_events.return_value = []
    
    # Test limit too high
    connector.get_upcoming_events("test@example.com", limit=100)
    assert mock_data_access.get_upcoming_events.call_args[0] == (1, 25)
    mock_data_access.get_upcoming_events.reset_mock()
    
    # Test limit=0 becomes default (5) due to "limit or 5"
    connector.get_upcoming_events("test@example.com", limit=0)
    assert mock_data_access.get_upcoming_events.call_args[0] == (1, 5)


def test_get_upcoming_events_paged_success(connector, mock_data_access):
    """Test successful retrieval of paged upcoming events."""
    mock_data_access.get_user_id_by_email.return_value = 1
    expected_events = [{"ID": 1, "Title": "Event 1"}]
    mock_data_access.get_upcoming_events_paged.return_value = expected_events
    
    result = connector.get_upcoming_events_paged("test@example.com", limit=5, offset=0)
    
    assert result == expected_events
    mock_data_access.get_upcoming_events_paged.assert_called_once_with(1, 5, 0)


def test_get_upcoming_events_paged_limit_clamping(connector, mock_data_access):
    """Test that paged limit is properly clamped."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_upcoming_events_paged.return_value = []
    
    # Test limit too high
    connector.get_upcoming_events_paged("test@example.com", limit=100, offset=0)
    assert mock_data_access.get_upcoming_events_paged.call_args[0] == (1, 50, 0)
    mock_data_access.get_upcoming_events_paged.reset_mock()
    
    # Test limit=0 becomes default (5) due to "limit or 5"
    connector.get_upcoming_events_paged("test@example.com", limit=0, offset=0)
    assert mock_data_access.get_upcoming_events_paged.call_args[0] == (1, 5, 0)
    mock_data_access.get_upcoming_events_paged.reset_mock()
    
    # Test offset negative
    connector.get_upcoming_events_paged("test@example.com", limit=5, offset=-5)
    assert mock_data_access.get_upcoming_events_paged.call_args[0] == (1, 5, 0)


def test_get_upcoming_events_count_success(connector, mock_data_access):
    """Test successful retrieval of upcoming events count."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_upcoming_events_count.return_value = 10
    
    result = connector.get_upcoming_events_count("test@example.com")
    
    assert result == 10
    mock_data_access.get_upcoming_events_count.assert_called_once_with(1)


def test_get_total_hours_success(connector, mock_data_access):
    """Test successful retrieval of total hours."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_total_hours.return_value = 25.5
    
    result = connector.get_total_hours("test@example.com")
    
    assert result == 25.5
    mock_data_access.get_total_hours.assert_called_once_with(1)


def test_get_completed_events_count_success(connector, mock_data_access):
    """Test successful retrieval of completed events count."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_completed_events_count.return_value = 5
    
    result = connector.get_completed_events_count("test@example.com")
    
    assert result == 5
    mock_data_access.get_completed_events_count.assert_called_once_with(1)


def test_get_completed_events_success(connector, mock_data_access):
    """Test successful retrieval of completed events."""
    mock_data_access.get_user_id_by_email.return_value = 1
    expected_events = [{"ID": 1, "Title": "Past Event 1"}]
    mock_data_access.get_completed_events.return_value = expected_events
    
    result = connector.get_completed_events("test@example.com", limit=50)
    
    assert result == expected_events
    mock_data_access.get_completed_events.assert_called_once_with(1, 50)


def test_get_completed_events_limit_clamping(connector, mock_data_access):
    """Test that completed events limit is properly clamped."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_completed_events.return_value = []
    
    # Test limit too high
    connector.get_completed_events("test@example.com", limit=200)
    assert mock_data_access.get_completed_events.call_args[0] == (1, 100)
    mock_data_access.get_completed_events.reset_mock()
    
    # Test limit=0 becomes default (50) due to "limit or 50"
    connector.get_completed_events("test@example.com", limit=0)
    assert mock_data_access.get_completed_events.call_args[0] == (1, 50)


def test_get_badges_success(connector, mock_data_access):
    """Test successful retrieval of badges."""
    mock_data_access.get_user_id_by_email.return_value = 1
    expected_badges = [{"ID": 1, "Name": "Badge 1"}]
    mock_data_access.get_badges.return_value = expected_badges
    
    result = connector.get_badges("test@example.com")
    
    assert result == expected_badges
    mock_data_access.get_badges.assert_called_once_with(1)


def test_get_dashboard_success(connector, mock_data_access):
    """Test successful retrieval of dashboard data."""
    mock_data_access.get_user_id_by_email.return_value = 1
    mock_data_access.get_upcoming_events.return_value = [{"ID": 1, "Title": "Event 1"}]
    mock_data_access.get_upcoming_events_count.return_value = 1
    mock_data_access.get_total_hours.return_value = 10.5
    mock_data_access.get_completed_events_count.return_value = 5
    mock_data_access.get_badges.return_value = [{"ID": 1, "Name": "Badge 1"}]
    
    result = connector.get_dashboard("test@example.com", limit=5)
    
    assert "upcoming_events" in result
    assert "upcoming_count" in result
    assert "total_hours" in result
    assert "completed_events" in result
    assert "badges" in result
    assert result["upcoming_count"] == 1
    assert result["total_hours"] == 10.5
    assert result["completed_events"] == 5

