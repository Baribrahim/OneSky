import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from events.routes import bp
from data_access import DataAccess
from datetime import timedelta, date

def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config["TESTING"] = True
    app.register_blueprint(bp)
    return app

@pytest.fixture(autouse=True)
def mock_db_connection():
    """Auto-use fixture to mock pymysql.connect to prevent real DB connections."""
    with patch('data_access.pymysql.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        yield mock_connect

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

# ---------------- ROUTE TESTS ---------------- #

@patch("events.routes.data_access.get_location", return_value=["London", "Manchester"])
def test_filter_events(mock_get_location, client):
    response = client.get("/api/events/filter_events")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["city"] == "London"

@patch("events.routes.data_access.get_filtered_events")
def test_get_filtered_events(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": 1, "name": "Charity Run", "Image_path": "images/run.jpg"}]
    response = client.get("/api/events/events?keyword=charity&location=London")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["name"] == "Charity Run"
    assert "Image_url" in data[0]

@patch("events.routes.data_access.get_filtered_events")
def test_search_events(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": 2, "name": "Beach Cleanup"}]
    response = client.get("/api/events/search?keyword=beach&location=Brighton")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["name"] == "Beach Cleanup"

@patch("events.routes.data_access.get_filtered_events", return_value=[])
def test_get_filtered_events_empty(mock_get_filtered_events, client):
    response = client.get("/api/events/events?keyword=nonexistent&location=Nowhere")
    assert response.status_code == 200
    assert response.get_json() == []

@patch("events.routes.data_access.get_filtered_events")
def test_get_filtered_events_no_params(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": 1, "name": "Default Event"}]
    response = client.get("/api/events/events")
    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Default Event"

@patch("events.routes.data_access.get_filtered_events")
def test_image_url_added(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": 1, "name": "Charity Run", "Image_path": "images/run.jpg"}]
    response = client.get("/api/events/events")
    data = response.get_json()
    assert "Image_url" in data[0]
    assert data[0]["Image_url"].endswith("images/run.jpg")

@patch("events.routes.data_access.get_location", return_value=[])
def test_filter_events_empty(mock_get_location, client):
    response = client.get("/api/events/filter_events")
    assert response.status_code == 200
    assert response.get_json() == []

@patch("events.routes.data_access.get_filtered_events", side_effect=Exception("DB error"))
def test_get_filtered_events_db_error(mock_get_filtered_events, client):
    response = client.get("/api/events/events")
    assert response.status_code == 500
    assert "error" in response.get_json()

@patch("events.routes.data_access.get_filtered_events")
def test_get_filtered_events_invalid_date(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = []
    response = client.get("/api/events/events?startDate=invalid-date")
    assert response.status_code == 200
    assert response.get_json() == []

@patch("events.routes.data_access.get_filtered_events")
def test_image_url_contains_host(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": 1, "name": "Charity Run", "Image_path": "images/run.jpg"}]
    response = client.get("/api/events/events")
    data = response.get_json()
    assert data[0]["Image_url"].startswith("http://")

@patch("events.routes.data_access.get_filtered_events")
def test_search_events_all_params(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": 3, "name": "Full Filter Event"}]
    response = client.get("/api/events/search?keyword=test&location=London&date=2025-11-04")
    assert response.get_json()[0]["name"] == "Full Filter Event"

@patch("events.routes.data_access.get_filtered_events")
def test_get_filtered_events_large_result(mock_get_filtered_events, client):
    mock_get_filtered_events.return_value = [{"id": i, "name": f"Event {i}"} for i in range(100)]
    response = client.get("/api/events/events")
    assert len(response.get_json()) == 100

# ---------------- DATAACCESS TESTS ---------------- #


# ---------------------------
# Test get_location()
# ---------------------------
@patch('data_access.pymysql.connect')
def test_get_location_sorted_unique(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"LocationCity": "London"},
        {"LocationCity": "Manchester"},
        {"LocationCity": "London"}
    ]
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_location()
    assert sorted(result) == ["London", "Manchester"]
    assert mock_cursor.fetchall.called

@patch('data_access.pymysql.connect')
def test_get_location_db_error(mock_connect):
    mock_connect.side_effect = Exception("DB error")
    dao = DataAccess()
    result = dao.get_location()
    assert result == []  # Should return empty list on error

# ---------------------------
# Test get_filtered_events()
# ---------------------------
@patch('data_access.pymysql.connect')
def test_get_filtered_events_with_params(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"ID": 1, "Title": "Charity Run", "About": "Help", "Date": date.today(),
         "StartTime": "10:00", "EndTime": "12:00", "LocationCity": "London",
         "Address": "Street", "LocationPostcode": "AB12", "Capacity": 50,
         "Image_path": "images/run.jpg", "CauseName": "Health", "TagName": "Fitness"}
    ]
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_filtered_events(keyword="charity", location="London", start_date="2025-11-04", end_date="2025-11-10")
    assert len(result) == 1
    assert result[0]["Title"] == "Charity Run"
    assert "Image_path" in result[0]

@patch('data_access.pymysql.connect')
def test_get_filtered_events_default_date(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_filtered_events(keyword=None, location=None)
    assert isinstance(result, list)
    assert mock_cursor.execute.called

@patch('data_access.pymysql.connect')
def test_get_filtered_events_db_error(mock_connect):
    mock_connect.side_effect = Exception("DB error")
    dao = DataAccess()
    result = dao.get_filtered_events(keyword="test")
    assert result == []

# ---------------------------
# Test get_event_by_id()
# ---------------------------
@patch('data_access.pymysql.connect')
def test_get_event_by_id_found(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "ID": 1, "Title": "Charity Run", "About": "Help", "Activities": "Run",
        "RequirementsBring": "Shoes", "RequirementsProvided": "Water",
        "Date": date.today(), "StartTime": "10:00", "EndTime": "12:00",
        "LocationCity": "London", "Latitude": "51.5", "Longitude": "-0.1",
        "Address": "Street", "LocationPostcode": "AB12", "Capacity": 50,
        "Image_path": "images/run.jpg", "CauseName": "Health", "TagName": "Fitness"
    }
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_event_by_id(1)
    assert result["Title"] == "Charity Run"
    assert "Latitude" in result

@patch('data_access.pymysql.connect')
def test_get_event_by_id_not_found(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_event_by_id(999)
    assert result is None

@patch('data_access.pymysql.connect')
def test_get_event_by_id_db_error(mock_connect):
    mock_connect.side_effect = Exception("DB error")
    dao = DataAccess()
    result = dao.get_event_by_id(1)
    assert result is None

# ---------------------------
# Test get_event_schedule()
# ---------------------------
@patch('data_access.pymysql.connect')
def test_get_event_schedule_with_timedelta(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"Time": timedelta(hours=1, minutes=30), "Title": "Intro", "Description": "Welcome"}
    ]
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_event_schedule(1)
    assert result[0]["Time"] == "01:30:00"

@patch('data_access.pymysql.connect')
def test_get_event_schedule_empty(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    dao = DataAccess()
    result = dao.get_event_schedule(1)
    assert result == []

@patch('data_access.pymysql.connect')
def test_get_event_schedule_db_error(mock_connect):
    mock_connect.side_effect = Exception("DB error")
    dao = DataAccess()
    result = dao.get_event_schedule(1)
    assert result == []
