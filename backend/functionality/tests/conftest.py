"""
Pytest configuration and shared fixtures for badge tests.
"""

import pytest
import sys
import os
from unittest.mock import Mock

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_data_access():
    """Create a mock DataAccess object for testing."""
    return Mock()


@pytest.fixture
def sample_badges():
    """Sample badge data for testing."""
    return [
        {
            "ID": 1,
            "Name": "Event Starter",
            "Description": "Registered for 1 upcoming events.",
            "IconURL": "/src/assets/badges/firstStep.png"
        },
        {
            "ID": 2,
            "Name": "Event Enthusiast",
            "Description": "Registered for 5 upcoming events.",
            "IconURL": "/src/assets/badges/eduEnthusiast.png"
        },
        {
            "ID": 3,
            "Name": "First Step",
            "Description": "Completed your first volunteering event.",
            "IconURL": "/src/assets/badges/firstStep.png"
        },
        {
            "ID": 4,
            "Name": "Volunteer Veteran",
            "Description": "Completed 10 volunteering events.",
            "IconURL": "/src/assets/badges/volunteerVetran.png"
        },
        {
            "ID": 5,
            "Name": "Marathon Helper",
            "Description": "Contributed 20+ total volunteering hours.",
            "IconURL": "/src/assets/badges/marathonVolunteer.png"
        },
        {
            "ID": 6,
            "Name": "Weekend Warrior",
            "Description": "Completed an event on a Saturday or Sunday.",
            "IconURL": "/src/assets/badges/weekendWarrior.png"
        }
    ]


@pytest.fixture
def sample_user_stats():
    """Sample user statistics for testing."""
    return {
        "upcoming_events": 3,
        "completed_events": 2,
        "total_hours": 15.0,
        "has_weekend_event": True
    }


@pytest.fixture
def sample_badge_progress():
    """Sample badge progress data for testing."""
    return {
        "event_starter": {"required": 1, "current": 3, "earned": True},
        "event_enthusiast": {"required": 5, "current": 3, "earned": False},
        "first_step": {"required": 1, "current": 2, "earned": True},
        "volunteer_veteran": {"required": 10, "current": 2, "earned": False},
        "marathon_helper": {"required": 20, "current": 15.0, "earned": False},
        "weekend_warrior": {"required": 1, "current": 1, "earned": True}
    }
