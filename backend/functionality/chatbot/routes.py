"""
Chatbot Routes
Flask blueprint for chatbot endpoints
"""
from flask import Blueprint, request, jsonify, g
from flask_cors import CORS
from .connector import ChatbotConnector
from auth.routes import token_required

bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")
CORS(bp, supports_credentials=True)


@bp.route("/chat", methods=["POST"])
@token_required
def chat():
    """
    POST /api/chatbot/chat
    Body: {"message": "user message here"}
    Returns: {"response": "bot response", "category": "events|teams|badges|impact|general"}
    """
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    user_email = g.current_user.get("sub")

    try:
        connector = ChatbotConnector()
        response, category = connector.process_message(message, user_email)

        return jsonify({
            "response": response,
            "category": category
        }), 200

    except ValueError as ve:
        print(f"Chatbot configuration error: {ve}")
        return jsonify({
            "error": "Chatbot configuration error. Please check OPENAI_API_KEY is set.",
            "details": str(ve)
        }), 500
    except Exception as e:
        print(f"Chatbot error: {e}")
        print(f"Error type: {type(e).__name__}")
        return jsonify({
            "error": "Sorry, I encountered an error. Please try again.",
            "details": str(e)[:200]
        }), 500
