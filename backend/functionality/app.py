# app.py
from flask import Flask, jsonify, redirect, url_for, request, current_app
from flask_cors import CORS
import jwt

# Import blueprints from feature packages
from auth.routes import bp as auth_bp
from events.routes import bp as events_bp
from dashboard.routes import bp as dashboard_bp
from teams.routes import bp as teams_bp
from badges.routes import bp as badges_bp
from chatbot.routes import bp as chatbot_bp


from chatbot.socket_chat import socketio


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "supersecret"

    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://localhost:3000",
                    "http://localhost:5174",
                ]
            }
        },
    )

    # Register feature blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(badges_bp)
    app.register_blueprint(chatbot_bp)

    @app.route("/")
    def root():
        token = request.cookies.get("access_token")
        if not token:
            # no cookie → not logged in
            return redirect(url_for("auth.login_page"))

        try:
            jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
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
    socketio.init_app(
        app,
        cors_allowed_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:5174",
        ],
    )

    # IMPORTANT: run with socketio, not app.run
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
