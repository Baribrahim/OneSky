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

def list_teams(all=False):
    """
    Lists all teams (newest first) or all joined/owned teams depending on flags.
    Returns: { teams: [...], count: n }
    """
    try:
        user_email = g.current_user.get("sub", "User")
        if all:
            items = connector.browse_all_teams(user_email)
        else:
            items = connector.browse_joined_teams(user_email)
        teams_out = [
            {
                "id": t["ID"],
                "name": t["Name"],
                "description": t.get("Description"),
                "department": t.get("Department"),
                "owner_user_id": t["OwnerUserID"],
                "join_code": t["JoinCode"],
                "is_active": t.get("IsActive", 1),
                "is_owner": t.get("IsOwner", 1),
                
            }
            for t in items 
        ]

        # #Return only the teams the user is the owner of
        # if owner:
        #     teams_out = [t for t in teams_out if t["is_owner"] == 1]

        return jsonify({"teams": teams_out, "count": len(teams_out)}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Could not load teams"}), 500


# POST /teams -> create a team
@bp.post("")
@require_auth
def create_team():
    """
    Creates a team for the authenticated user.
    Body: { name, description, department }
    """
    payload = request.get_json(silent=True) or {}
    creator_email = g.current_user.get("sub")

    try:
        row = connector.create_team(
            creator_email=creator_email,
            name=payload.get("name"),
            description=payload.get("description"),
            department=payload.get("department"),
        )

        response = {
            "id": row["ID"],
            "name": row["Name"],
            "description": row.get("Description"),
            "department": row.get("Department"),
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
@bp.get("")
@require_auth
def list_all_teams():
    return list_teams(all=True)



"""Signs the user up to the selected team"""
@bp.route("/join", methods=["POST"])
@require_auth 
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


@bp.route("/joined", methods=["GET"])
@require_auth
def list_joined_teams():
   return list_teams(all=False)

# POST /api/teams/<team_id>/delete
@bp.post("/<int:team_id>/delete")
@require_auth
def delete_team(team_id: int):
    """
    Delete a team by ID.
    """
    try:
        connector.delete_team(team_id)
        return jsonify({"message": f"Team {team_id} deleted successfully."}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not delete team"}), 500


# POST /api/teams/<team_id>/leave
@bp.post("/<int:team_id>/leave")
@require_auth
def leave_team(team_id: int):
    """
     user leaves a team by ID.
    """
    try:
        user_email = g.current_user.get("sub", "User")
        connector.leave_team(user_email, team_id)
        return jsonify({"message": f"User {user_email} left team {team_id} successfully."}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not leave team"}), 500


# GET /api/teams/<team_id>/members
@bp.get("/<int:team_id>/members")
@require_auth
def get_team_members(team_id: int):
    """
    Returns all members of a team.
    """
    try:
        members = connector.read_all_team_members(team_id)
        members_out = [
            {
                "id": m["ID"],
                "first_name": m.get("FirstName"),
                "last_name": m.get("LastName"),
                "email": m.get("Email"),
                "profile_img_path": m.get("ProfileImgPath"),
            }
            for m in members
        ]
        return jsonify({"members": members_out, "count": len(members_out)}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not fetch team members"}), 500
