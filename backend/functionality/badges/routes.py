"""
Badge Routes - API endpoints for badge functionality.
Handles HTTP requests for badge operations including retrieval and awarding.
"""

import json
from flask import Blueprint, request, jsonify, g
from .connector import BadgeConnector
from auth.routes import token_required
from flask_cors import CORS

bp = Blueprint("api_badges", __name__, url_prefix="/api/badges")
CORS(bp, supports_credentials=True)


@bp.route("", methods=["GET"])
@token_required
def get_user_badges():
    """
    Get all badges earned by the current user.
    
    Returns:
        JSON response with user's badges or error message
    """
    try:
        user_email = g.current_user.get("sub")
        if not user_email:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Get user ID from email
        connector = BadgeConnector()
        user_id = connector.data_access.get_user_id_by_email(user_email)
        
        if not user_id:
            return jsonify({"error": "User not found"}), 404
        
        badges = connector.get_user_badges(user_id)
        return jsonify({"badges": badges}), 200
        
    except Exception as e:
        print(f"Badge routes: Error getting user badges - {e}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/all", methods=["GET"])
@token_required
def get_all_badges():
    """
    Get all available badges in the system.
    
    Returns:
        JSON response with all badges or error message
    """
    try:
        connector = BadgeConnector()
        badges = connector.get_all_badges()
        return jsonify({"badges": badges}), 200
        
    except Exception as e:
        print(f"Badge routes: Error getting all badges - {e}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/check", methods=["POST"])
@token_required
def check_and_award_badges():
    """
    Check user's activity and award appropriate badges.
    This endpoint should be called after user actions that might earn badges.
    
    Returns:
        JSON response with newly awarded badges or error message
    """
    try:
        user_email = g.current_user.get("sub")
        if not user_email:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Get user ID from email
        connector = BadgeConnector()
        user_id = connector.data_access.get_user_id_by_email(user_email)
        
        if not user_id:
            return jsonify({"error": "User not found"}), 404
        
        # Check and award badges
        newly_awarded = connector.check_and_award_event_badges(user_id)
        
        return jsonify({
            "message": "Badge check completed",
            "newly_awarded": newly_awarded,
            "count": len(newly_awarded)
        }), 200
        
    except Exception as e:
        print(f"Badge routes: Error checking badges - {e}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/progress", methods=["GET"])
@token_required
def get_badge_progress():
    """
    Get user's progress towards earning badges.
    
    Returns:
        JSON response with badge progress information
    """
    try:
        user_email = g.current_user.get("sub")
        if not user_email:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Get user ID from email
        connector = BadgeConnector()
        user_id = connector.data_access.get_user_id_by_email(user_email)
        
        if not user_id:
            return jsonify({"error": "User not found"}), 404
        
        progress = connector.get_user_badge_progress(user_id)
        return jsonify({"progress": progress}), 200
        
    except Exception as e:
        print(f"Badge routes: Error getting badge progress - {e}")
        return jsonify({"error": "Internal server error"}), 500


@bp.route("/award", methods=["POST"])
@token_required
def award_badge():
    """
    Manually award a specific badge to a user.
    This endpoint is for administrative purposes or special cases.
    
    Request body should contain:
        - badge_id: ID of the badge to award
        
    Returns:
        JSON response with success/failure message
    """
    try:
        data = request.get_json(silent=True) or {}
        badge_id = data.get("badge_id")
        
        if not badge_id:
            return jsonify({"error": "Badge ID is required"}), 400
        
        user_email = g.current_user.get("sub")
        if not user_email:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Get user ID from email
        connector = BadgeConnector()
        user_id = connector.data_access.get_user_id_by_email(user_email)
        
        if not user_id:
            return jsonify({"error": "User not found"}), 404
        
        # Award the badge
        success, message = connector.award_badge_to_user(user_id, badge_id)
        
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        print(f"Badge routes: Error awarding badge - {e}")
        return jsonify({"error": "Internal server error"}), 500

