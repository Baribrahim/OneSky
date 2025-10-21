import datetime
from functools import wraps
import json
import jwt
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, g
from .connector import Connector
from auth.routes import token_required
from flask_cors import CORS
import json
from data_access import DataAccess

bp = Blueprint("api_events", __name__, url_prefix="/api/events")
CORS(bp, supports_credentials=True)

@bp.route("", methods=["GET"])
@token_required
def get_events():
    con = Connector()
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
    con = Connector()
    con.register_user_for_event(user_email, event_id)
    return jsonify({"message": "Successfully registered for event!"}), 200

@bp.route("/signup-status", methods=["GET"])
@token_required
def check_signup_status():
    user_email = g.current_user.get("sub", "User")
    con = Connector()
    is_signed_up = con.user_signed_up_for_events(user_email)
    return jsonify(is_signed_up), 200

@bp.route("/unregister", methods=["POST"])
@token_required
def unregister_from_event():
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    
    if not event_id:
        return jsonify({"error": "Missing event_id"}), 400
    
    user_email = g.current_user.get("sub", "User")
    con = Connector()
    con.unregister_user_from_event(user_email, event_id)
    return jsonify({"message": "Successfully unregistered for event"}), 200


# Reanna's addition for search and filter functionality #

data_access = DataAccess()

@bp.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    locations = data_access.get_location()
    return jsonify([{"city": loc} for loc in locations])


# @bp.route('/events', methods=['GET'])
# def get_filtered_events():
#     location = request.args.get('location') or None
#     events = data_access.get_all_events(location)
#     print("===Events===")
#     print(events)
#     return jsonify(events)

@bp.route('/events', methods=['GET'])
def get_filtered_events_route():
    keyword = request.args.get('keyword') or None
    location = request.args.get('location') or None
    date = request.args.get('date') or None

    events = data_access.get_filtered_events(keyword, location, date)
    return jsonify(events)


@bp.route('/search', methods=['GET'])
def search_events():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    date = request.args.get('date', '')
    events = data_access.search_events(keyword, location, date)
    return jsonify(events)