# dashboard/routes.py
from flask import Blueprint, request, jsonify, g, render_template
from dashboard.connector import DashboardConnector
from auth.routes import token_required 


bp = Blueprint("dashboard", __name__, url_prefix="")
dc = DashboardConnector()

# Impact: stats summary
@bp.get("/dashboard/impact")
@token_required
def dashboard_impact():
    """
    GET /dashboard/impact
    Returns user's impact summary:
    - total_hours: total hours from past events
    - events_completed: number of past events
    - counts: upcoming_events, badges
    - first_name: for greeting
    - as_of: timestamp for clarity
    """
    from datetime import datetime, timezone

    email = g.current_user.get("sub")
    first_name = g.current_user.get("first_name", "User")
    limit = request.args.get("limit", default=5, type=int)

    try:
        data = dc.get_dashboard(email, limit=limit)

        total_hours = float(data.get("total_hours", 0.0))
        events_completed = int(data.get("completed_events", 0))
        upcoming = data.get("upcoming_events", [])
        badges = data.get("badges", [])
        upcoming_count = int(data.get("upcoming_count", len(upcoming)))

        payload = {
            "first_name": first_name,
            "total_hours": total_hours,
            "events_completed": events_completed,
            "counts": {
                "upcoming_events": upcoming_count,
                "badges": len(badges),
            },
            "as_of": datetime.now(timezone.utc).isoformat()
        }
        return jsonify(payload), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("ERROR: ", e)
        return jsonify({"error": "Something went wrong"}), 500


# UPCOMING: timeline/cards data
@bp.get("/dashboard/upcoming")
@token_required
def dashboard_upcoming():
    """
    GET /dashboard/upcoming?limit=5&offset=0
    Returns:
      - upcoming_events: [ ...items... ]
      - count: len(items)
      - total: total upcoming events (no limit)
      - has_more: whether more items exist beyond this page
    """
    email = g.current_user.get("sub")
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    try:
        items = dc.get_upcoming_events_paged(email, limit=limit, offset=offset)

        # Deduplicate events by ID, preferring team registrations
        deduped = {}
        for item in items:
            event_id = item["ID"]
            team_name = item.get("RegistrationType")
            
            # If event not seen yet, or current item has a team (overrides Individual)
            if event_id not in deduped or (team_name != "Individual"):
                deduped[event_id] = item

        # Keep the order same as original
        items = list(deduped.values())

        total = dc.get_upcoming_events_count(email)
        has_more = (offset + len(items)) < total

        return jsonify({
            "upcoming_events": items,
            "count": len(items),
            "total": int(total),
            "has_more": bool(has_more)
        }), 200


    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Error: ", e)
        return jsonify({"error": "Something went wrong"}), 500


# ACHIEVEMENTS: badges with icon/title/description
@bp.get("/dashboard/achievements")
@token_required
def dashboard_achievements():
    """
    GET /dashboard/achievements
    Returns badges for the user (with IconURL if available).
    """
    email = g.current_user.get("sub")

    try:
        badges = dc.get_badges(email)
        # Badges are: ID, Name, Description, IconURL
        return jsonify({"badges": badges, "count": len(badges)}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception:
        return jsonify({"error": "Something went wrong"}), 500

@bp.get("/dashboard/completed-events")
@token_required
def dashboard_completed_events():
    """
    GET /dashboard/completed-events
    Returns user's completed events list.
    """
    email = g.current_user.get("sub")
    limit = request.args.get("limit", default=50, type=int)

    try:
        completed_events = dc.get_completed_events(email, limit=limit)
        return jsonify({"completed_events": completed_events}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except Exception:
        return jsonify({"error": "Something went wrong"}), 500

@bp.get("/dashboard_page")
@token_required
def dashboard_page():
    """
    Renders dashboard.html with user data (for Jinja testing).
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
            events_completed=int(data.get("completed_events", 0)),
            badges=data.get("badges", []),
        ), 200

    except ValueError as ve:
        return render_template(
            "dashboard.html",
            title="Dashboard",
            first_name=first_name,
            upcoming_events=[],
            events_completed=0,
            badges=[],
            error=str(ve),
        ), 400

    except Exception:
        return render_template(
            "dashboard.html",
            title="Dashboard",
            first_name=first_name,
            upcoming_events=[],
            events_completed=0,
            badges=[],
            error="Could not load dashboard data.",
        ), 500