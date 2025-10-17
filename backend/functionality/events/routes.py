import datetime
from functools import wraps
import jwt
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, g
from .connector import Connector
from auth.routes import token_required


bp = Blueprint("events", __name__, url_prefix="/events")

@bp.route("/")
@token_required
def get_events():
    con = Connector()
    data = con.extract_event_details()
    first_name = g.current_user.get("first_name", "User")    
    return render_template("events.html", data=data, first_name=first_name)


@bp.route("/signup", methods=["POST"])
@token_required  
def signup_event():
    event_id = request.form.get("event_id")
    user_email = g.current_user.get("sub", "User") 
    con = Connector()
    con.register_user_for_event(user_email, event_id)
    flash("Successfully registered for event!", "success")
    return redirect(url_for("events.get_events"))

# Reanna's addition for search and filter functionality #
data_access = DataAccess()

@bp.route('/filter_events', methods=['GET', 'POST'])
def filter_events():
    locations = data_access.get_location()
    # return render_template('event_page.html', locations=locations, events=[])
    return jsonify({"locations": locations, "events": []})


@bp.route('/events', methods=['GET'])
def get_events():
    location = request.args.get('location')
    events = data_access.get_all_events(location)
    locations = data_access.get_location()
    # return render_template('event_page.html', events=events, locations=locations)
    return jsonify({"events": events, "locations": locations})


@bp.route('/search', methods=['GET'])
def search_events():
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    date = request.args.get('date')

    events = data_access.search_events(keyword, location, date)
    locations = data_access.get_location()
    # return render_template('event_page.html', events=events, locations=locations)
    return jsonify({"events": events, "locations": locations})