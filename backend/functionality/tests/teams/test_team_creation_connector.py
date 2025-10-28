import pytest
from teams.connector import TeamConnector

class FakeDA:
    """Fake DataAccess for connector unit tests (no real DB)."""
    def __init__(self):
        self.teams = []
        self.users = {"owner@example.com": 1}

    # --- user lookup ---
    def get_user_id_by_email(self, email):
        return self.users.get(email)

    # --- uniqueness check ---
    def get_team_by_join_code(self, code):
        return next((t for t in self.teams if t["JoinCode"] == code), None)

    # --- create + list ---
    def create_team(self, name, description, department, capacity, owner_user_id, join_code):
        row = {
            "ID": len(self.teams) + 1,
            "Name": name.strip(),
            "Description": description,
            "Department": department,
            "Capacity": capacity,
            "OwnerUserID": owner_user_id,
            "JoinCode": join_code,
            "IsActive": 1,
        }
        self.teams.append(row)
        return row

    def list_all_teams(self, user_email =None):
        # emulate DB: newest first
        return sorted(self.teams, key=lambda t: t["ID"], reverse=True)

def test_create_team_success():
    da = FakeDA()
    tc = TeamConnector(da=da)

    row = tc.create_team(
        creator_email="owner@example.com",
        name="  Alpha  ",
        description="A team",
        department="Tech",
        capacity=20,
    )
    assert row["Name"] == "Alpha"
    assert row["OwnerUserID"] == 1
    assert len(row["JoinCode"]) == 8

def test_create_team_validation_errors():
    da = FakeDA()
    tc = TeamConnector(da=da)

    with pytest.raises(ValueError, match="Name is required"):
        tc.create_team("owner@example.com", "", "", None, None)

    with pytest.raises(ValueError, match="at most 120"):
        tc.create_team("owner@example.com", "A"*121, "", None, None)

    with pytest.raises(ValueError, match="positive integer"):
        tc.create_team("owner@example.com", "Ok", "", None, "x")

    with pytest.raises(ValueError, match=">= 1"):
        tc.create_team("owner@example.com", "Ok", "", None, 0)

def test_browse_all_teams_order_and_empty_state():
    da = FakeDA()
    tc = TeamConnector(da=da)

    # empty
    items = tc.browse_all_teams("owner@example.com")
    assert items == []

    # seed a few
    tc.create_team("owner@example.com", "Team 1", None, None, None)
    tc.create_team("owner@example.com", "Team 2", None, None, None)
    tc.create_team("owner@example.com", "Team 3", None, None, None)

    items2 = tc.browse_all_teams("owner@example.com")
    assert [t["Name"] for t in items2] == ["Team 3", "Team 2", "Team 1"]
