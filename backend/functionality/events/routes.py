import datetime
from functools import wraps
import jwt
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, g
from .connector import Connector
from auth.routes import token_required
from flask_cors import CORS
import json


bp = Blueprint("events", __name__, url_prefix="/events")
CORS(bp, supports_credentials=True)

# not being used
# @bp.route("/")
# @token_required
# def get_events():
#     con = Connector()
#     data = con.extract_event_details()
#     first_name = g.current_user.get("first_name", "User")    
#     return render_template("events.html", data=data, first_name=first_name)

# # not being used
# @bp.route("/signup", methods=["POST"])
# @token_required  
# def signup_event():
#     event_id = request.form.get("event_id")
#     user_email = g.current_user.get("sub", "User") 
#     con = Connector()
#     con.register_user_for_event(user_email, event_id)
#     flash("Successfully registered for event!", "success")
#     return redirect(url_for("events.get_events"))

# Reanna's addition for search and filter functionality #
from data_access import DataAccess
data_access = DataAccess()

@bp.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    locations = data_access.get_location()
    return jsonify([{"city": loc} for loc in locations])


@bp.route('/events', methods=['GET'])
def get_filtered_events():
    location = request.args.get('location')
    events = data_access.get_all_events(location)
    # locations = data_access.get_location()
    print("===Events===")
    print(events)
    return jsonify(events)


@bp.route('/search', methods=['GET'])
def search_events():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    date = request.args.get('date', '')
    events = data_access.search_events(keyword, location, date)
    return jsonify(events)