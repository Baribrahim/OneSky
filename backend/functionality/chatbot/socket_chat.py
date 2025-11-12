"""
socket_chat.py
WebSocket / Socket.IO bridge for the OneSky chatbot.

- Listens for: "chatbot_message"
- Streams back: "chatbot_response"
- NOW: extracts user_email from the same JWT cookie ("access_token") in Flask routes
"""

import os
import jwt
from flask import request, current_app
from flask_socketio import SocketIO, join_room

from .connector import ChatbotConnector

# create socketio instance (init_app happens in app.py)
socketio = SocketIO(cors_allowed_origins="*")

# single chatbot instance
chatbot = ChatbotConnector()


def _get_user_email_from_cookie() -> str | None:
    """
    Try to read the JWT from the 'access_token' cookie,
    decode it with the Flask SECRET_KEY, and return the 'sub' (email).
    """
    token = request.cookies.get("access_token")
    if not token:
        return None

    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        return None
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        # auth uses "sub" as the user email
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@socketio.on("connect")
def handle_connect():
    # just to see that socket connects
    print(f"[socket] client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    print(f"[socket] client disconnected: {request.sid}")


@socketio.on("chatbot_message")
def handle_chatbot_message(payload):
    """
    Incoming message from client.
    payload looks like: {"message": "show my badges"}
    user_email is taken from JWT cookie so we can fetch user's data.
    """
    user_message = (payload or {}).get("message", "")
    # try to get email from cookie/JWT
    user_email = (payload or {}).get("user_email") or _get_user_email_from_cookie()

    if not user_message.strip():
        socketio.emit(
            "chatbot_response",
            {
                "response": "Please type a message.",
                "category": "general",
                "done": True,
            },
            room=request.sid,
        )
        return

    # join a room so we can emit back to just this client
    room = request.sid
    join_room(room)

    print(f"[socket] message from {user_email or 'anonymous'}: {user_message}")

    # define how the connector should emit
    def emit_fn(event_name: str, data: dict, room: str = None):
        if room:
            socketio.emit(event_name, data, room=room)
        else:
            socketio.emit(event_name, data)

    # run streaming logic
    chatbot.process_message_stream(
        user_message=user_message,
        user_email=user_email,
        emit_fn=emit_fn,
        room=room,
    )
