# dashboard/routes.py
from flask import Blueprint, request, jsonify, g, render_template
from dashboard.connector import DashboardConnector
from auth.routes import token_required  # reuse your decorator

bp = Blueprint("dashboard", __name__, url_prefix="")
dc = DashboardConnector()

@bp.get("/dashboard")
@token_required
def dashboard_api():
    """
    GET /dashboard?limit=5
    Returns JSON for React or Postman.
    """
    email = g.current_user.get("sub")
    first_name = g.current_user.get("first_name", "User")
    limit = request.args.get("limit", default=5, type=int)

    try:
        data = dc.get_dashboard(email, limit=limit)
        payload = {
            "first_name": first_name,
            "upcoming_events": data.get("upcoming_events", []),
            "total_hours": float(data.get("total_hours", 0.0)),
            "badges": data.get("badges", []),
            "counts": {
                "upcoming_events": len(data.get("upcoming_events", [])),
                "badges": len(data.get("badges", [])),
            },
        }
        return jsonify(payload), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception:
        return jsonify({"error": "Something went wrong"}), 500

@bp.get("/dashboard_page")
@token_required
def dashboard_page():
    """
    GET /api/dashboard_page
    Renders dashboard.html with user data (for Jinja testing).
    Uses same backend logic as API.
    """
    email = g.current_user.get("sub")
    first_name = g.current_user.get("first_name", "User")

    try:
        data = dc.get_dashboard(email, limit=5)
        return render_template(
            "dashboard.html",
            title="Dashboard",
            first_name=first_name,
            upcoming_events=data.get("upcoming_events", []),
            total_hours=float(data.get("total_hours", 0.0)),
            badges=data.get("badges", []),
        ), 200

    except ValueError as ve:
        return render_template(
            "dashboard.html",
            title="Dashboard",
            first_name=first_name,
            upcoming_events=[],
            total_hours=0.0,
            badges=[],
            error=str(ve),
        ), 400

    except Exception:
        return render_template(
            "dashboard.html",
            title="Dashboard",
            first_name=first_name,
            upcoming_events=[],
            total_hours=0.0,
            badges=[],
            error="Could not load dashboard data.",
        ), 500