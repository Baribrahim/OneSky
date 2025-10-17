# app.py
from flask import Flask, jsonify, redirect, url_for, request, current_app
from flask_cors import CORS
import jwt


# Import blueprints from feature packages
from auth.routes import bp as auth_bp
from events.routes import bp as events_bp
# from search.routes import bp as search_bp           # (later)
# from eventregistration.routes import bp as er_bp     # (later)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "supersecret"
    CORS(app,
        supports_credentials=True,  # if you want the browser to also send/receive cookies
        resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}})

    # Register feature blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    # app.register_blueprint(search_bp)
    # app.register_blueprint(er_bp)

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
    app.run(host="127.0.0.1", port=5000, debug=True)


