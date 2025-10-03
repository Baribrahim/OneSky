# app.py
from flask import Flask, jsonify
from flask_cors import CORS

# Import blueprints from feature packages
from filter.routes import bp as filter_bp
# from search.routes import bp as search_bp           # (later)
# from eventregistration.routes import bp as er_bp     # (later)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = "supersecret"
    CORS(app)

    # Register feature blueprints
    app.register_blueprint(filter_bp)
    # app.register_blueprint(search_bp)
    # app.register_blueprint(er_bp)

    @app.get("/")
    def home():
        return jsonify({
            "message": "Flask API is running",
            "routes": ["/health", "/auth/register_page", "/auth/register"]
        })

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/favicon.ico")
    def favicon():
        return ("", 204)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)