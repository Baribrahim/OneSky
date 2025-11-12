import datetime
from datetime import UTC
from functools import wraps

import jwt
from flask import Blueprint, render_template, request, flash, jsonify, current_app, redirect, url_for, g
from .connector import Connector

bp = Blueprint("auth", __name__, url_prefix="")

TOKEN_COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 3600  # 1 hour

"""Token Handling"""
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token_from_request()
        if not token:
            return redirect(url_for("auth.login_page"))

        try:
            decoded = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])  # NOSONAR - Configuration key name, not a hard-coded credential
            g.current_user = decoded  # store user info in flask.g
        except jwt.ExpiredSignatureError:
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for("auth.login_page"))
        except jwt.InvalidTokenError:
            flash("Invalid session. Please log in.", "danger")
            return redirect(url_for("auth.login_page"))

        return f(*args, **kwargs)
    return decorated


def _get_token_from_request():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]
    return request.cookies.get(TOKEN_COOKIE_NAME)

def generate_token(user_data: dict):
    payload = {
        "sub": user_data["email"],
        "first_name": user_data["first_name"],
        "exp": datetime.datetime.now(UTC) + datetime.timedelta(hours=1)
    }
    secret = current_app.config.get("SECRET_KEY")  # NOSONAR - Configuration key name, not a hard-coded credential
    if not isinstance(secret, str) or not secret:
        raise RuntimeError("SECRET_KEY must be a non-empty string")  # NOSONAR - Error message, not a credential

    token = jwt.encode(payload, secret, algorithm="HS256")
    return token if isinstance(token, str) else token.decode("utf-8")

"""Me Route - this is for react to get user info"""
@bp.route("/api/me", methods=["GET"])
@token_required
def me():
    from flask import g
    return jsonify({
        "email": g.current_user.get("sub"),
        "first_name": g.current_user.get("first_name")
    })


"""Home Route"""
@bp.route('/home')
@token_required
def home():
    first_name = g.current_user.get("first_name", "User")
    return render_template("home.html", title="Home", first_name=first_name)


"""Register Routes"""
@bp.route("/register_page")
def register_page():
    return render_template('register.html', title='Register')

@bp.route("/register", methods=["POST"])
def register():
    # support both JSON and form submissions
    data = request.get_json(silent=True) or request.form
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    ca = Connector()
    success, message = ca.add_user(email, password, first_name, last_name)
    if not success:
        # JSON returns 400; form re-renders with error
        if request.is_json:
            return jsonify({"error": message}), 400
        return render_template("register.html", title="Register", error=message)

    # Check for badges after successful registration
    try:
        from badges.connector import BadgeConnector
        badge_connector = BadgeConnector()
        user_id = ca.get_user_id_by_email(email)
        if user_id:
            badge_connector.check_and_award_event_badges(user_id)
    except Exception as e:
        print(f"Error checking badges after registration: {e}")

    token = generate_token({"email": email, "first_name": first_name})

    if request.is_json:
        resp = jsonify({"token": token})
    else:
        resp = redirect(url_for("auth.home"))

    resp.set_cookie(
        TOKEN_COOKIE_NAME,
        token,
        httponly=True,
        secure=current_app.config.get("COOKIE_SECURE", False),
        samesite=current_app.config.get("COOKIE_SAMESITE", "Lax"),
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    return resp

"""Login/Logout Routes"""
@bp.route("/login_page")
def login_page():
    return render_template('login.html', title='Login')

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    ca = Connector()
    user = ca.verify_user_by_password(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Check for badges after successful login
    try:
        from badges.connector import BadgeConnector
        badge_connector = BadgeConnector()
        user_id = ca.get_user_id_by_email(email)
        if user_id:
            badge_connector.check_and_award_event_badges(user_id)
    except Exception as e:
        print(f"Error checking badges after login: {e}")

    token = generate_token({"email": user["Email"], "first_name": user["FirstName"]})

    # Decide response shape
    if request.is_json:
        resp = jsonify({"token": token})          # React expects JSON
    else:
        resp = redirect(url_for("auth.home"))     # Jinja expects redirect

    # Always set cookie (Jinja depends on it; fine for React too if same-origin/CORS configured)
    resp.set_cookie(
        TOKEN_COOKIE_NAME,
        token,
        httponly=True,
        secure=current_app.config.get("COOKIE_SECURE", False),
        samesite=current_app.config.get("COOKIE_SAMESITE", "Lax"),
        max_age=COOKIE_MAX_AGE,
        path="/",
    )
    return resp

@bp.route("/logout")
@token_required
def logout():
    resp = redirect(url_for("auth.login_page"))
    resp.delete_cookie(TOKEN_COOKIE_NAME, path="/")
    return resp

