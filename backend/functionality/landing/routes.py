from flask import Blueprint, jsonify

bp = Blueprint("landing", __name__, url_prefix="/landing")

@bp.route("/", methods=["GET"])
def get_landing_info():
    return jsonify({
        "title": "Welcome to Sky Volunteering",
        "tagline": "Connect. Contribute. Celebrate.",
        "description": "Discover volunteering opportunities, join teams, and make an impact together.",
        "features": [
            "Browse events by location, date, and tags",
            "Register easily for events",
            "Join teams or create your own",
            "Sign up to events with your team",
            "Use your dashboard to track upcoming events, past events and total hours volunteered",
            "Have some friendly competition with our Leaderboard",
            "Earn badges as you go"
        ]
    })