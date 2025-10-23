import json
from flask import Blueprint, request, jsonify, g
from .connector import Connector
from auth.routes import token_required


bp = Blueprint("api_teams", __name__, url_prefix="/api/teams")

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
    con = Connector()
    if(con.verify_team_code(team_id, join_code)):
        con.add_user_to_team(user_email, team_id)
        return jsonify({"message": "Successfully registered for team"}), 200
    else:
        return jsonify({"error": "Invalid code"}), 400
    

@bp.route("/join-status", methods=["GET"])
@token_required
def check_join_status():
    user_email = g.current_user.get("sub", "User")
    con = Connector()
    joined_teams = con.user_joined_teams(user_email)
    return jsonify(joined_teams), 200


