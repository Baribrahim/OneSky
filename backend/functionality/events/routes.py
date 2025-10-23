import datetime
from functools import wraps
import json

import jwt
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, g
from .connector import Connector
from auth.routes import token_required


bp = Blueprint("api_events", __name__, url_prefix="/api/events")

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
    con = Connector()
    con.unregister_user_from_event(user_email, event_id)
    return jsonify({"message": "Successfully unregistered for event"}), 200