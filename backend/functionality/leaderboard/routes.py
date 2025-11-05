from flask import Blueprint, jsonify, g
from leaderboard.connector import LeaderboardConnector
from auth.routes import token_required

bp = Blueprint("leaderboard", __name__, url_prefix="/api/leaderboard")
lc = LeaderboardConnector()

@bp.get("")
@token_required
def ranked_users():
    """Returns users in descending order of their rank score."""
    try:
        email = g.current_user.get("sub")
        users = lc.get_ordered_users(email)
        return jsonify({"users": users}), 200
    except Exception as e:
        print(f"Error in ranked_users: {e}")
        return jsonify({"error": "Something went wrong"}), 500

@bp.get("my-rank")
@token_required
def my_rank():
    """Returns users current ranking in leaderboard."""
    try:
        email = g.current_user.get("sub")
        rank = lc.get_user_current_rank(email)
        return jsonify({"currentRank": rank}), 200
    except Exception as e:
        print(f"Error in my_rank: {e}")
        return jsonify({"error": "Something went wrong"}), 500
