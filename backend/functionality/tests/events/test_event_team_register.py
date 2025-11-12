# Joining a team functionality Testing

#Connector Methods
import os
from unittest.mock import patch, MagicMock
import pytest
from events.connector import EventConnector
from events import routes
from tests.test_validation import _login_get_token, _register_user, TEST_PASSWORD

# Use environment variable for SECRET_KEY in tests, with test-only fallback
SECRET = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")  # NOSONAR - Test-only fallback, not a production credential

@pytest.fixture(autouse=True)
def mock_data_access():
    """Auto-use fixture to mock all DataAccess instances and prevent real DB connections."""
    with patch('data_access.pymysql.connect') as mock_connect, \
         patch('auth.connector.DataAccess') as mock_auth_da_class, \
         patch('badges.connector.DataAccess') as mock_badge_da_class, \
         patch('events.connector.DataAccess') as mock_events_da_class:
        
        # Mock pymysql connection to prevent real DB connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock DataAccess instances for connectors
        mock_auth_da_instance = MagicMock()
        mock_badge_da_instance = MagicMock()
        mock_events_da_instance = MagicMock()
        
        mock_auth_da_class.return_value = mock_auth_da_instance
        mock_badge_da_class.return_value = mock_badge_da_instance
        mock_events_da_class.return_value = mock_events_da_instance
        
        # Set up default return values for registration/login flow
        mock_auth_da_instance.user_exists.return_value = False
        mock_auth_da_instance.get_user_id_by_email.return_value = 1
        mock_auth_da_instance.get_user_by_email.return_value = {
            "ID": 1,
            "Email": "test@sky.uk",
            "Password": b"$2b$12$hashedpassword",
            "FirstName": "Test",
            "LastName": "User"
        }
        mock_auth_da_instance.verify_user_by_password.return_value = {
            "ID": 1,
            "Email": "test@sky.uk",
            "FirstName": "Test",
            "LastName": "User"
        }
        mock_badge_da_instance.check_and_award_event_badges.return_value = []
        
        yield {
            'auth': mock_auth_da_instance,
            'badge': mock_badge_da_instance,
            'events': mock_events_da_instance
        }

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = SECRET  # NOSONAR - Test-only configuration, value comes from env var or test fallback
    with app.test_client() as client:
        yield client


"""Connector methods"""

def test_extract_team_event_details_calls_dao_correctly():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.read_user_teams_with_registration_status.return_value = [
            {"ID": 1, "Name": "Team Alpha", "isRegistered": 1},
            {"ID": 2, "Name": "Team Beta", "isRegistered": 0}
        ]
        connector = EventConnector()
        user_email = "user@example.com"
        event_id = 123

        # Act
        result = connector.extract_team_event_details(user_email, event_id)

        # Assert
        mock_dao_instance.read_user_teams_with_registration_status.assert_called_once_with(event_id, user_email)
        assert result == [
            {"ID": 1, "Name": "Team Alpha", "isRegistered": 1},
            {"ID": 2, "Name": "Team Beta", "isRegistered": 0}
        ]


def test_extract_team_event_details_raises_when_dao_fails():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.read_user_teams_with_registration_status.side_effect = Exception("DB error")
        connector = EventConnector()

        # Act & Assert
        try:
            connector.extract_team_event_details("user@example.com", 1)
        except Exception as e:
            assert str(e) == "DB error"
        else:
            assert False, "Expected Exception not raised"


def test_register_team_for_event_calls_dao_correctly():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        connector = EventConnector()
        team_id = 55
        event_id = 77

        # Act
        connector.register_team_for_event(team_id, event_id)

        # Assert
        mock_dao_instance.insert_team_to_event_registration.assert_called_once_with(team_id, event_id)


def test_register_team_for_event_raises_when_dao_fails():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.insert_team_to_event_registration.side_effect = Exception("Insert failed")
        connector = EventConnector()

        # Act & Assert
        try:
            connector.register_team_for_event(1, 2)
        except Exception as e:
            assert str(e) == "Insert failed"
        else:
            assert False, "Expected Exception not raised"


"""Routes Methods"""

def test_successful_team_signup(client):
    """POST /api/events/signup-team returns 200 on success"""
    # Arrange
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    with patch.object(routes.con, "register_team_for_event", return_value=None) as mock_register:
        # Act
        response = client.post(
            "/api/events/signup-team",
            json={"event_id": 1, "team_id": 2},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Successfully registered for event!"
        mock_register.assert_called_once_with(2, 1)


def test_signup_team_missing_event_id_returns_400(client):
    """Should return 400 if event_id missing"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    response = client.post(
        "/api/events/signup-team",
        json={"team_id": 2},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing event_id"


def test_signup_team_missing_team_id_returns_400(client):
    """Should return 400 if team_id missing"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    response = client.post(
        "/api/events/signup-team",
        json={"event_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing team_id"


# ---------------------------------------------------------------------
# /api/events/<event_id>/available-teams
# ---------------------------------------------------------------------

def test_get_available_teams_success(client):
    """GET /api/events/<id>/available-teams returns available teams"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    mock_teams = [
        {"ID": 1, "Name": "Team Alpha", "isRegistered": 1},
        {"ID": 2, "Name": "Team Beta", "isRegistered": 0}
    ]

    with patch.object(routes.con, "extract_team_event_details", return_value=mock_teams):
        response = client.get(
            "/api/events/1/available-teams",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert "teams" in data
        assert len(data["teams"]) == 2
        assert data["teams"][0]["Name"] == "Team Alpha"


# ---------------------------------------------------------------------
# /api/events/signup-status
# ---------------------------------------------------------------------

def test_check_signup_status_success(client):
    """GET /api/events/signup-status returns user's signed up events"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    mock_signed_up_events = [
        {"ID": 1, "Title": "Event 1", "Date": "2024-01-01"},
        {"ID": 2, "Title": "Event 2", "Date": "2024-02-01"}
    ]

    with patch.object(routes.con, "user_signed_up_for_events", return_value=mock_signed_up_events):
        response = client.get(
            "/api/events/signup-status",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["Title"] == "Event 1"


def test_check_signup_status_empty(client):
    """GET /api/events/signup-status returns empty list when user has no signups"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    with patch.object(routes.con, "user_signed_up_for_events", return_value=[]):
        response = client.get(
            "/api/events/signup-status",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0


# ---------------------------------------------------------------------
# /api/events/unregister
# ---------------------------------------------------------------------

def test_unregister_from_event_success(client):
    """POST /api/events/unregister returns 200 on success"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    with patch.object(routes.con, "unregister_user_from_event", return_value=None) as mock_unregister:
        response = client.post(
            "/api/events/unregister",
            json={"event_id": 1},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Successfully unregistered for event"
        # Check that it was called with the correct event_id and any email
        assert mock_unregister.called
        call_args = mock_unregister.call_args[0]
        assert call_args[1] == 1  # event_id should be 1


def test_unregister_from_event_missing_event_id(client):
    """POST /api/events/unregister returns 400 if event_id missing"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, TEST_PASSWORD)

    response = client.post(
        "/api/events/unregister",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing event_id"