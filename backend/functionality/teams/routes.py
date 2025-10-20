# teams/routes.py
from flask import Blueprint, request, jsonify, g
from auth.routes import token_required
from teams.connector import TeamConnector

bp = Blueprint("teams", __name__, url_prefix="")
connector = TeamConnector()

# POST /teams -> create a team
@bp.post("/teams")
@token_required
def create_team():
    """
    Creates a team for the authenticated user.
    Body: { name, description, department, capacity }
    """
    payload = request.get_json(silent=True) or {}
    creator_email = g.current_user.get("sub")

    try:
        row = connector.create_team(
            creator_email=creator_email,
            name=payload.get("name"),
            description=payload.get("description"),
            department=payload.get("department"),
            capacity=payload.get("capacity"),
        )

        response = {
            "id": row["ID"],
            "name": row["Name"],
            "description": row.get("Description"),
            "department": row.get("Department"),
            "capacity": row.get("Capacity"),
            "owner_user_id": row["OwnerUserID"],
            "join_code": row["JoinCode"],
            "is_active": row.get("IsActive", 1),
        }
        return jsonify(response), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception:
        return jsonify({"error": "Could not create team"}), 500


# GET /teams -> list ALL teams (newest first)
@bp.get("/teams")
@token_required
def list_teams():
    """
    Lists all teams (newest first).
    Returns: { teams: [...], count: n }
    """
    try:
        items = connector.browse_all_teams()
        teams_out = [
            {
                "id": t["ID"],
                "name": t["Name"],
                "description": t.get("Description"),
                "department": t.get("Department"),
                "capacity": t.get("Capacity"),
                "owner_user_id": t["OwnerUserID"],
                "join_code": t["JoinCode"],
                "is_active": t.get("IsActive", 1),
            }
            for t in items
        ]
        return jsonify({"teams": teams_out, "count": len(teams_out)}), 200

    except Exception:
        return jsonify({"error": "Could not load teams"}), 500
