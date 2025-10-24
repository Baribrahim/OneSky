# teams/routes.py
from functools import wraps
from flask import Blueprint, request, jsonify, g
from auth.routes import token_required
from teams.connector import TeamConnector

bp = Blueprint("api_teams", __name__, url_prefix="/api/teams")
connector = TeamConnector()


def require_auth(f):
    """
    Indirection layer so token_required can be monkeypatched in tests.
    We defer applying token_required until request time.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        decorated = token_required(f)
        return decorated(*args, **kwargs)
    return wrapped


# POST /teams -> create a team
@bp.post("/teams")
@require_auth
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
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not create team"}), 500


# GET /teams -> list ALL teams (newest first)
@bp.get("/teams")
@require_auth
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



"""Signs the user up to the selected team"""
@bp.route("/join", methods=["POST"])
@token_required  
def signup_to_team():
    data = request.get_json(silent=True) or {}
    team_id = data.get("team_id")
    join_code = data.get("join_code")
    print(f"Received join_code: {join_code}")
    print(f"Received team_id: {team_id}")

    if not team_id:
        return jsonify({"error": "Missing team_id"}), 400

    if not join_code:
        return jsonify({"error": "Missing join_code"}), 400

    user_email = g.current_user.get("sub", "User") 
    print(f"g.current_user: {g.current_user}")
    if(connector.verify_team_code(team_id, join_code)):
        connector.add_user_to_team(user_email, team_id)
        return jsonify({"message": "Successfully registered for team"}), 200
    else:
        return jsonify({"error": "Invalid code"}), 400
    

# @bp.route("/join-status", methods=["GET"])
# @token_required
# def check_join_status():
#     user_email = g.current_user.get("sub", "User")
#     con = Connector()
#     joined_teams = con.user_joined_teams(user_email)
#     return jsonify(joined_teams), 200