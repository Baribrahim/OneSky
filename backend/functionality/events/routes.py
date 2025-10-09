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
