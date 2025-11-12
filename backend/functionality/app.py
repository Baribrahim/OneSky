# app.py
import os
from flask import Flask, jsonify, redirect, url_for, request, current_app
from flask_cors import CORS
import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import blueprints from feature packages
from auth.routes import bp as auth_bp
from events.routes import bp as events_bp
from dashboard.routes import bp as dashboard_bp
from teams.routes import bp as teams_bp
from badges.routes import bp as badges_bp
from profile.routes import bp as profile_bp
from leaderboard.routes import bp as leaderboard_bp
from chatbot.routes import bp as chatbot_bp
from landing.routes import bp as landing_bp
from chatbot.socket_chat import socketio


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    secret_key = os.getenv("SECRET_KEY")  # NOSONAR - This is reading from env, not hard-coding
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable must be set")  # NOSONAR - Error message, not a credential
    app.config["SECRET_KEY"] = secret_key  # NOSONAR - Configuration key name, value comes from env var

    # Get allowed origins from environment or use defaults
    allowed_origins = os.getenv("CORS_ORIGINS", "http://35.210.202.5:81,http://localhost:3000,http://localhost:5174").split(",")
    
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/*": {
                "origins": allowed_origins
            }
        },
    )

    # Register feature blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(badges_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(profile_bp)
    # app.register_blueprint(search_bp)
    # app.register_blueprint(er_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(landing_bp)


    @app.route("/")
    def root():
        token = request.cookies.get("access_token")
        if not token:
            # no cookie → not logged in
            return redirect(url_for("auth.login_page"))

        try:
            jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])  # NOSONAR - Configuration key name, not a hard-coded credential
            # valid token → go home
            return redirect(url_for("auth.home"))
        except jwt.ExpiredSignatureError:
            return redirect(url_for("auth.login_page"))
        except jwt.InvalidTokenError:
            return redirect(url_for("auth.login_page"))

    return app


if __name__ == "__main__":
    app = create_app()

    # IMPORTANT: init socketio on the app
    # Get allowed origins from environment or use defaults
    socketio_origins = os.getenv("CORS_ORIGINS", "http://35.210.202.5:81,http://localhost:3000,http://localhost:5174").split(",")
    socketio.init_app(
        app,
        cors_allowed_origins=socketio_origins,
    )

    # IMPORTANT: run with socketio, not app.run
    socketio.run(app, host="0.0.0.0", port=5001, debug=False, allow_unsafe_werkzeug=True)
