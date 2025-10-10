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
