"""
Test suite for LeaderboardConnector using pytest.
Tests cover all LeaderboardConnector methods with mocked data access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from leaderboard.connector import LeaderboardConnector
from data_access import DataAccess


@pytest.fixture
def mock_data_access():
    """Fixture for mocked DataAccess."""
    return Mock(spec=DataAccess)


@pytest.fixture
def connector(mock_data_access):
    """Fixture for LeaderboardConnector with mocked data access."""
    connector = LeaderboardConnector(dao=mock_data_access)
    return connector


def test_get_ordered_users_success(connector, mock_data_access):
    """Test successful retrieval of ordered users."""
    expected_users = [
        {"ID": 1, "FirstName": "User1", "RankScore": 100},
        {"ID": 2, "FirstName": "User2", "RankScore": 90}
    ]
    mock_data_access.read_user_by_ordered_rank_score.return_value = expected_users
    
    result = connector.get_ordered_users("test@example.com")
    
    assert result == expected_users
    mock_data_access.update_rank_score.assert_called_once_with("test@example.com")
    mock_data_access.read_user_by_ordered_rank_score.assert_called_once()


def test_get_ordered_users_empty(connector, mock_data_access):
    """Test get_ordered_users when no users exist."""
    mock_data_access.read_user_by_ordered_rank_score.return_value = []
    
    result = connector.get_ordered_users("test@example.com")
    
    assert result == []
    mock_data_access.update_rank_score.assert_called_once_with("test@example.com")
    mock_data_access.read_user_by_ordered_rank_score.assert_called_once()


def test_get_user_stats_success(connector, mock_data_access):
    """Test successful retrieval of user stats."""
    expected_stats = {
        "completed_events": 5,
        "total_hours": 20.0,
        "badges": 3
    }
    mock_data_access.read_user_stats.return_value = expected_stats
    
    result = connector.get_user_stats("test@example.com")
    
    assert result == expected_stats
    mock_data_access.read_user_stats.assert_called_once_with("test@example.com")


def test_get_user_stats_none(connector, mock_data_access):
    """Test get_user_stats when user has no stats."""
    mock_data_access.read_user_stats.return_value = None
    
    result = connector.get_user_stats("test@example.com")
    
    assert result is None
    mock_data_access.read_user_stats.assert_called_once_with("test@example.com")


def test_get_user_current_rank_success(connector, mock_data_access):
    """Test successful retrieval of user's current rank."""
    mock_data_access.read_user_rank.return_value = 5
    
    result = connector.get_user_current_rank("test@example.com")
    
    assert result == 5
    mock_data_access.read_user_rank.assert_called_once_with("test@example.com")


def test_get_user_current_rank_none(connector, mock_data_access):
    """Test get_user_current_rank when user has no rank."""
    mock_data_access.read_user_rank.return_value = None
    
    result = connector.get_user_current_rank("test@example.com")
    
    assert result is None
    mock_data_access.read_user_rank.assert_called_once_with("test@example.com")


def test_connector_initialization_with_dao():
    """Test LeaderboardConnector initialization with provided DataAccess."""
    mock_dao = Mock(spec=DataAccess)
    connector = LeaderboardConnector(dao=mock_dao)
    
    assert connector.dao == mock_dao


def test_connector_initialization_without_dao():
    """Test LeaderboardConnector initialization without provided DataAccess."""
    connector = LeaderboardConnector()
    
    assert connector.dao is not None
    assert isinstance(connector.dao, DataAccess)


def test_get_ordered_users_updates_rank_score(connector, mock_data_access):
    """Test that get_ordered_users updates rank score before retrieving."""
    mock_data_access.read_user_by_ordered_rank_score.return_value = []
    
    connector.get_ordered_users("test@example.com")
    
    # Verify update_rank_score is called before read_user_by_ordered_rank_score
    calls = mock_data_access.method_calls
    update_call = [c for c in calls if c[0] == 'update_rank_score']
    read_call = [c for c in calls if c[0] == 'read_user_by_ordered_rank_score']
    
    assert len(update_call) == 1
    assert len(read_call) == 1
    # Verify order: update should be called before read
    assert calls.index(update_call[0]) < calls.index(read_call[0])

