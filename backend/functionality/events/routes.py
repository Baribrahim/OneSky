import datetime
from functools import wraps
import json
import jwt
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, g
from .connector import EventConnector
from auth.routes import token_required
from flask_cors import CORS
from data_access import DataAccess

bp = Blueprint("api_events", __name__, url_prefix="/api/events")
CORS(bp, supports_credentials=True)
con = EventConnector()

@bp.route("", methods=["GET"])
@token_required
def get_events():
    data = con.extract_event_details()
    resp = json.dumps(data, default=str)
    return resp, 200

@bp.route("/signup", methods=["POST"])
@token_required  
def signup_event():
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")

    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400

    user_email = g.current_user.get("sub", "User") 
    con.register_user_for_event(user_email, event_id)
    
    # Check for badges after successful event registration
    try:
        from badges.connector import BadgeConnector
        badge_connector = BadgeConnector()
        user_id = con.get_user_id_by_email(user_email)
        if user_id:
            newly_awarded = badge_connector.check_and_award_event_badges(user_id)
            if newly_awarded:
                print(f"User {user_email} earned {len(newly_awarded)} new badges!")
    except Exception as e:
        print(f"Error checking badges after event signup: {e}")
    
    return jsonify({"message": "Successfully registered for event!"}), 200

@bp.route("/signup-status", methods=["GET"])
@token_required
def check_signup_status():
    user_email = g.current_user.get("sub", "User")
    signed_up_events = con.user_signed_up_for_events(user_email)
    return jsonify(signed_up_events), 200

@bp.route("/unregister", methods=["POST"])
@token_required
def unregister_from_event():
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    
    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400
    
    user_email = g.current_user.get("sub", "User")
    con.unregister_user_from_event(user_email, event_id)
    return jsonify({"message": "Successfully unregistered for event"}), 200


# Reanna's addition for search and filter functionality #

data_access = DataAccess()

@bp.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    locations = data_access.get_location()
    return jsonify([{"city": loc} for loc in locations])


@bp.route('/events', methods=['GET'])
def get_filtered_events_route():
    keyword = request.args.get('keyword') or None
    location = request.args.get('location') or None
    start_date = request.args.get('startDate') or None
    end_date = request.args.get('endDate') or None
    events = data_access.get_filtered_events(keyword, location, start_date, end_date)


  # Add full image URL for each event
    
    for event in events:
        path = event.get('Image_path') or event.get('image_path')
        event['Image_url'] = f"{request.host_url}static/{path}" if path else None


    return jsonify(events)


@bp.route('/search', methods=['GET'])
def search_events():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    date = request.args.get('date', '')

    events = data_access.search_events(keyword, location, date)
    return jsonify(events)

@bp.route("/signup-team", methods=["POST"])
@token_required  
def signup_team_event():
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    team_id = data.get("team_id")

    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400
    
    if not team_id:
        return jsonify({"error": "Missing team_id"}), 400

    con.register_team_for_event(team_id, event_id)
    return jsonify({"message": "Successfully registered for event!"}), 200

@bp.route("/<int:event_id>/available-teams", methods=["GET"])
@token_required
def get_users_unregistered_teams(event_id):
    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400
    user_email = g.current_user.get("sub")
    data = con.extract_team_unregistered_details(user_email, event_id)
    return jsonify({"teams": data}), 200