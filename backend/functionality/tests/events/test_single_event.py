import pytest
from unittest.mock import patch

# ---------------------------
# /events/<id>
# ---------------------------

@patch("events.routes.data_access.get_event_by_id")
def test_get_event_found(mock_get_event_by_id, client):
    mock_get_event_by_id.return_value = {
        "ID": 1, "Title": "Charity Run", "LocationCity": "London", "Date": "2025-11-04"
    }
    response = client.get("/api/events/events/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["Title"] == "Charity Run"
    assert set(data.keys()) >= {"ID", "Title", "LocationCity"}

@patch("events.routes.data_access.get_event_by_id", return_value=None)
def test_get_event_not_found(mock_get_event_by_id, client):
    response = client.get("/api/events/events/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Event not found"

def test_get_event_invalid_id(client):
    response = client.get("/api/events/events/abc")
    assert response.status_code == 404  # Flask handles invalid int

@patch("events.routes.data_access.get_event_by_id", side_effect=Exception("DB error"))
def test_get_event_db_error(mock_get_event_by_id, client):
    response = client.get("/api/events/events/1")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "DB error"

# ---------------------------
# /events/<event_id>/schedule
# ---------------------------

@patch("events.routes.data_access.get_event_schedule")
def test_get_schedule_found(mock_get_event_schedule, client):
    mock_get_event_schedule.return_value = [
        {"Time": "10:00", "Title": "Intro", "Description": "Welcome"}
    ]
    response = client.get("/api/events/events/1/schedule")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["Title"] == "Intro"

@patch("events.routes.data_access.get_event_schedule", return_value=[])
def test_get_schedule_empty(mock_get_event_schedule, client):
    response = client.get("/api/events/events/1/schedule")
    assert response.status_code == 200
    assert response.get_json() == []

@patch("events.routes.data_access.get_event_schedule", side_effect=Exception("DB error"))
def test_get_schedule_db_error(mock_get_event_schedule, client):
    response = client.get("/api/events/events/1/schedule")
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "DB error"

@patch("events.routes.data_access.get_event_schedule")
def test_get_schedule_large(mock_get_event_schedule, client):
    mock_get_event_schedule.return_value = [
        {"Time": "10:00", "Title": f"Session {i}", "Description": "Details"} for i in range(100)
    ]
    response = client.get("/api/events/events/1/schedule")
    data = response.get_json()
    assert len(data) == 100

@patch("events.routes.data_access.get_event_schedule")
def test_get_schedule_timedelta(mock_get_event_schedule, client):
    mock_get_event_schedule.return_value = [
        {"Time": "01:30:00", "Title": "Intro", "Description": "Welcome"}
    ]
    response = client.get("/api/events/events/1/schedule")
    data = response.get_json()
    assert data[0]["Time"] == "01:30:00"