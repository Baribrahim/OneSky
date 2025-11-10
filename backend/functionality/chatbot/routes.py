"""
Chatbot Routes
Flask blueprint for chatbot endpoints
"""
from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
from .connector import ChatbotConnector, PromptInjectionError
from auth.routes import token_required

bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")
CORS(bp, supports_credentials=True)


@bp.route("/chat", methods=["POST"])
@token_required
def chat():
    """
    POST /api/chatbot/chat
    Body: {"message": "user message here"}
    Returns: {
        "response": "...",
        "category": "events|teams|badges|impact|general",
        "events": [...],
        "teams": [...],
        "badges": [...],
        "team_events": [...]
    }
    """
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # from JWT (set by token_required)
    user_email = g.current_user.get("sub")

    try:
        connector = ChatbotConnector()
        (
            response_text,
            category,
            events_list,
            teams_list,
            badges_list,
            team_events_list,
        ) = connector.process_message(message, user_email)

        response_data = {
            "response": response_text,
            "category": category,
        }

        # If events are present, include them
        if events_list:
            response_data["events"] = events_list
            # if we have events, tell the frontend it's "events"
            if category != "events":
                response_data["category"] = "events"

        # If teams are present, include them
        if teams_list:
            response_data["teams"] = teams_list
            # only override category if the connector didn't already set it
            if category != "teams" and "events" not in response_data:
                response_data["category"] = "teams"

        # If badges are present, include them
        if badges_list:
            response_data["badges"] = badges_list
            if category != "badges" and "events" not in response_data and "teams" not in response_data:
                response_data["category"] = "badges"

        # If team events are present, include them
        if team_events_list:
            response_data["team_events"] = team_events_list
            # don't force category change here — it's additional info

        return jsonify(response_data), 200

    except PromptInjectionError as pie:
        return jsonify({"error": "Message rejected", "details": str(pie)}), 400
    except ValueError as ve:
        print(f"Chatbot configuration error: {ve}")
        return (
            jsonify(
                {
                    "error": "Chatbot configuration error. Please check OPENAI_API_KEY is set.",
                    "details": str(ve),
                }
            ),
            500,
        )
    except Exception as e:
        print(f"Chatbot error: {e}")
        print(f"Error type: {type(e).__name__}")
        return (
            jsonify(
                {
                    "error": "Sorry, I encountered an error. Please try again.",
                    "details": str(e)[:200],
                }
            ),
            500,
        )
