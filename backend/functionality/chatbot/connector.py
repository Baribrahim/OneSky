"""
Chatbot Connector
- Supports OpenAI tool/function calling to decide which data-access method to run.
- Keeps the same output shape expected by the frontend (for HTTP).
- NOW also supports a socket-friendly streaming method to increase perceived speed.
"""

import os
import json
import calendar
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable

from dotenv import load_dotenv
from openai import OpenAI

from data_access import DataAccess
from .embedding_helper import EmbeddingHelper

load_dotenv()

# ---------------------------------------------------------------------
# Security / Prompt-injection safeguards
# ---------------------------------------------------------------------


class PromptInjectionError(ValueError):
    """Raised when a user message is deemed unsafe for processing."""


_FORBIDDEN_PATTERNS = [
    re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
    re.compile(r"reset\s+the\s+conversation", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"(?:disregard|forget)\s+all\s+prior\s+(?:responses|instructions)", re.IGNORECASE),
    re.compile(r"\b(database|schema|table|sql|drop table|truncate|delete from)\b", re.IGNORECASE),
]

_SPECIAL_CHARS = [
    "!", "@", "$", "%", "^", "*", "(", ")", "-", "_", '"', "'", ":", ";", "<", ">", "/", "\\", "~", "“", "”", "‘", "’",
]

# Module-level memory storage (shared-ish)
_short_term_memory: Dict[str, List[Dict[str, str]]] = {}
_long_term_memory: Dict[str, str] = {}

# ---------------------------------------------------------------------
# Shared system prompt
# ---------------------------------------------------------------------
SYSTEM_PROMPT = """You are OneSky Assistant, the helpful chatbot for OneSky — Sky's internal volunteering platform where employees can find volunteering opportunities, track impact, earn badges, and collaborate in teams.
All navigation and features can be accessed from the header menu at the top of the page.

When responding:
- Be concise, direct, and friendly — no filler or unrelated info.
- Only provide information relevant to the user's query.
- Use emoji sparingly when helpful (never excessive).
- Always stay within OneSky context — do not answer general or external questions.
- Do not end your responses with questions.

Navigation Menu (top of the page through the header):
- Home: Displays the user's dashboard — impact stats, upcoming events, earned badges, and featured events. To view completed events, click the "Completed Events" card on the dashboard.
- Events: Browse and search volunteering opportunities. Users can register individually or, if they own a team, register as a team by clicking "Register/Register as a team". Registered events appear on the Home dashboard.
- Teams: Manage and explore teams. Users can create a team (fill the form, share the join code) or browse existing teams to join.
- Logout: Click the logout button in the top-right corner of the header.

Note: When users mention "signing up for an event" or "registering," they mean registering for a volunteer event, not creating an account.

IMPORTANT FOR TOOL CALLING:
- If you call a tool that returns events, teams, badges, or stats, keep your final text reply SHORT (1–2 sentences). The UI will show the actual items as cards.
- Prefer personal/user-specific tools (like 'get_my_upcoming_events') if the user is clearly talking about "my" or "I".
- For completed/past events: Use 'get_my_completed_events' when the user asks about "completed events", "past events", "events I've done", "history", or "events I attended". Do NOT use 'get_my_upcoming_events' for completed events.
- If the user wants to browse generally (e.g. "show me events in London this weekend"), use the general event search tool.
- For time-based queries (e.g., "this weekend", "next week", "next month", "today", "tomorrow"), use the relative date expressions directly in the search_events tool parameters. The system will automatically convert them to proper dates. Examples:
  * "show events this weekend" → use start_date="this weekend", end_date="this weekend"
  * "events next week" → use start_date="next week" (or calculate Monday-Sunday range)
  * "events next month" → use start_date="next month", end_date="next month" (expands to full month range)
  * "events today" → use start_date="today", end_date="today"
- When suggesting teams to join: NEVER mention join codes. Users must obtain join codes directly from the team owner. Simply suggest the team and let users know they can contact the team owner for the join code.
- If the user asks about anything unrelated to OneSky (e.g., Sky corporate info, personal help, or non-volunteering topics, jokes, code in the prompt) reply politely:
"I'm sorry, I can only help with volunteering events and features on the OneSky platform."
"""

class ChatbotConnector:
    """
    Chatbot connector using OpenAI tool calling.
    Now has:
      - process_message(...)  -> for HTTP (existing)
      - process_message_stream(...) -> for sockets (new)
    """

    def __init__(self):
        self.dao = DataAccess()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.openai_client = OpenAI(api_key=api_key)
        # keep embedding helper because we may need semantic search inside tools
        self.embedding_helper = EmbeddingHelper(api_key)

        # instance-scoped memory (so tests don’t leak)
        self.short_term_memory: Dict[str, List[Dict[str, str]]] = {}
        self.long_term_memory: Dict[str, str] = {}

    def _sanitise_user_message(self, message: str) -> str:
        """Basic input sanitisation to reduce prompt-injection risks."""
        if not isinstance(message, str):
            raise PromptInjectionError("Message rejected due to unsafe content.")

        trimmed = message.strip()
        if not trimmed:
            raise PromptInjectionError("Message rejected due to unsafe content.")

        for pattern in _FORBIDDEN_PATTERNS:
            if pattern.search(trimmed):
                raise PromptInjectionError("Message rejected due to unsafe content.")

        sanitised = trimmed
        for char in _SPECIAL_CHARS:
            sanitised = sanitised.replace(char, "")

        sanitised = re.sub(r"\s{2,}", " ", sanitised).strip()

        if not sanitised:
            raise PromptInjectionError("Message rejected due to unsafe content.")

        return sanitised

    # ======================================================================
    # MAIN ENTRY POINT (HTTP)
    # ======================================================================
    def process_message(
        self,
        user_message: str,
        user_email: Optional[str] = None,
    ) -> Tuple[str, str, Optional[List[dict]], Optional[List[dict]], Optional[List[dict]], Optional[List[dict]]]:
        """
        Processes the user message using tool calling.
        This is the non-streaming version (for your current /api/chatbot/chat).
        Returns 6 values:
        (response_text, category, events, teams, badges, team_events)
        """
        sanitised_message = self._sanitise_user_message(user_message)

        # 1) Store user message in short-term memory
        if user_email:
            self._add_to_conversation_history(user_email, "user", sanitised_message)

        # 2) Personalization
        user_first_name = self._get_user_first_name(user_email) if user_email else None

        # 3) Build base messages (system + history + user)
        messages = [
            {"role": "system", "content": self._build_system_prompt(user_first_name)}
        ]
        if user_email:
            history = self._get_conversation_history(user_email)
            messages.extend(history)
        messages.append({"role": "user", "content": sanitised_message})

        # 4) First call: let the model decide whether to call a tool
        try:
            first_response = self.openai_client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages,
                tools=self._get_tools(),
                tool_choice="auto",  # let model decide
            )
        except Exception as e:
            print(f"OpenAI API error (first call): {e}")
            return (
                "Sorry, I'm having trouble processing your request right now.",
                "general",
                None,
                None,
                None,
                None,
            )

        if not first_response or not first_response.choices:
            return (
                "Sorry, I received an unexpected response from the AI.",
                "general",
                None,
                None,
                None,
                None,
            )

        assistant_msg = first_response.choices[0].message

        # If the model did NOT call a tool → just return its answer
        if not getattr(assistant_msg, "tool_calls", None):
            final_text = assistant_msg.content.strip() if assistant_msg.content else "Done."
            if user_email:
                self._add_to_conversation_history(user_email, "assistant", final_text)
            return final_text, "general", None, None, None, None

        # 5) If we’re here, the model asked to call one or more tools
        tool_calls = assistant_msg.tool_calls
        tool_outputs_for_model = []
        events_result: List[dict] = []
        teams_result: List[dict] = []
        badges_result: List[dict] = []
        team_events_result: List[dict] = []
        detected_category = "general"

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                tool_args = {}

            exec_result = self._execute_tool_call(tool_name, tool_args, user_email)

            # For the model: we pass the raw data as JSON (stringify everything)
            tool_outputs_for_model.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(exec_result.get("data", []), default=str),
                }
            )

            # For the frontend: collect separately
            result_type = exec_result.get("type")
            if result_type == "events":
                events_result = exec_result.get("data", [])
                detected_category = "events"
            elif result_type == "teams":
                teams_result = exec_result.get("data", [])
                detected_category = "teams"
            elif result_type == "badges":
                badges_result = exec_result.get("data", [])
                detected_category = "badges"
            elif result_type == "team_events":
                team_events_result = exec_result.get("data", [])
            elif result_type == "impact":
                detected_category = "impact"

        # 6) Second call: let the model phrase the answer
        try:
            second_messages = messages + [assistant_msg] + tool_outputs_for_model
            second_response = self.openai_client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=second_messages,
            )
            final_text = (
                second_response.choices[0].message.content.strip()
                if second_response and second_response.choices
                else "Done."
            )
        except Exception as e:
            print(f"OpenAI API error (second call): {e}")
            final_text = "Here are the details you asked for."

        # 7) Store assistant reply
        if user_email:
            self._add_to_conversation_history(user_email, "assistant", final_text)

        # 8) Return to frontend
        return (
            final_text,
            detected_category,
            events_result if events_result else None,
            teams_result if teams_result else None,
            badges_result if badges_result else None,
            team_events_result if team_events_result else None,
        )

    # ======================================================================
    # SOCKET-FRIENDLY STREAMING ENTRY POINT
    # ======================================================================
    def process_message_stream(
    self,
    user_message: str,
    user_email: str | None,
    emit_fn,
    room: str | None = None,
    ):
        """
        Streaming version for socket use.
        - Lets the model decide whether to call a tool (like get_my_events)
        - If a tool is called → execute it, show results fast
        - If no tool is called → respond directly
        - Streams text progressively to improve UX
        """
        try:
            sanitised_message = self._sanitise_user_message(user_message)
        except PromptInjectionError:
            rejection_payload = {
                "response": "Sorry, I can't process that request.",
                "category": "general",
                "done": True,
                "stream": True,
            }
            if room:
                emit_fn("chatbot_response", rejection_payload, room=room)
            else:
                emit_fn("chatbot_response", rejection_payload)
            return

        # Save user message in short-term memory (for conversational context)
        if user_email:
            self._add_to_conversation_history(user_email, "user", sanitised_message)

        user_first_name = self._get_user_first_name(user_email) if user_email else None

        # Construct message list with system prompt and chat history
        messages = [
            {"role": "system", "content": self._build_system_prompt(user_first_name)}
        ]
        if user_email:
            messages.extend(self._get_conversation_history(user_email))
        messages.append({"role": "user", "content": sanitised_message})

        detected_category = "general"

        # ---------------- First model call ----------------
        # The model decides if a tool (function) should be called
        try:
            first_response = self.openai_client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=messages,
                tools=self._get_tools(),
                tool_choice="auto",  # Let the model decide automatically
            )
        except Exception:
            # Handle API or connection errors gracefully
            err_payload = {
                "response": "Sorry, I couldn't process that right now.",
                "category": "general",
                "done": True,
                "stream": True,
            }
            if room:
                emit_fn("chatbot_response", err_payload, room=room)
            else:
                emit_fn("chatbot_response", err_payload)
            return

        # Handle empty/invalid responses
        if not first_response or not first_response.choices:
            done_payload = {
                "response": "Sorry, I received an empty response.",
                "category": "general",
                "done": True,
                "stream": True,
            }
            if room:
                emit_fn("chatbot_response", done_payload, room=room)
            else:
                emit_fn("chatbot_response", done_payload)
            return

        assistant_msg = first_response.choices[0].message

        # ---------------- CASE 1: No tool called ----------------
        # For general chat or conceptual platform questions
        if not getattr(assistant_msg, "tool_calls", None):
            final_text = (assistant_msg.content or "").strip() or "Okay."
            payload = {
                "response": final_text,
                "category": "general",
                "done": True,
                "stream": True,
                "final_text": final_text,
            }
            if room:
                emit_fn("chatbot_response", payload, room=room)
            else:
                emit_fn("chatbot_response", payload)

            # Save assistant reply in memory
            if user_email:
                self._add_to_conversation_history(user_email, "assistant", final_text)
            return

        # ---------------- CASE 2: Tool(s) called ----------------
        # The model wants to retrieve or search data via one of our defined tools
        tool_calls = assistant_msg.tool_calls
        tool_outputs_for_model = []
        events_result, teams_result, badges_result, team_events_result = [], [], [], []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                import json
                tool_args = json.loads(tool_call.function.arguments or "{}")
            except Exception:
                tool_args = {}

            # Execute the corresponding DataAccess method
            exec_result = self._execute_tool_call(tool_name, tool_args, user_email)

            # Pass tool results back to model (for second round)
            tool_outputs_for_model.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(exec_result.get("data", []), default=str),
                }
            )

            # Categorize results for frontend rendering
            result_type = exec_result.get("type")
            if result_type == "events":
                events_result = exec_result.get("data", [])
                detected_category = "events"
            elif result_type == "teams":
                teams_result = exec_result.get("data", [])
                detected_category = "teams"
            elif result_type == "badges":
                badges_result = exec_result.get("data", [])
                detected_category = "badges"
            elif result_type == "team_events":
                team_events_result = exec_result.get("data", [])
            elif result_type == "impact":
                detected_category = "impact"

        # Send partial results (cards) to frontend right away
        partial_payload = {
            "partial": True,
            "stream": True,
            "category": detected_category,
        }
        if events_result:
            partial_payload["events"] = events_result
        if teams_result:
            partial_payload["teams"] = teams_result
        if badges_result:
            partial_payload["badges"] = badges_result
        if team_events_result:
            partial_payload["team_events"] = team_events_result

        if room:
            emit_fn("chatbot_response", partial_payload, room=room)
        else:
            emit_fn("chatbot_response", partial_payload)

        # ---------------- Second model call ----------------
        # Now the model writes the natural-language summary based on tool results
        try:
            second_messages = messages + [assistant_msg] + tool_outputs_for_model
            second_response = self.openai_client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=second_messages,
            )
            final_text = (
                second_response.choices[0].message.content.strip()
                if second_response and second_response.choices
                else "Here are the details you asked for."
            )
        except Exception:
            final_text = "Here are the details you asked for."

        # Stream the text back in small chunks for a typing effect
        chunk_size = 30
        for i in range(0, len(final_text), chunk_size):
            piece = final_text[i : i + chunk_size]
            piece_payload = {
                "response": piece,
                "category": detected_category,
                "stream": True,
            }
            if room:
                emit_fn("chatbot_response", piece_payload, room=room)
            else:
                emit_fn("chatbot_response", piece_payload)

        # Send a final "done" signal so frontend stops loading
        done_payload = {
            "response": None,
            "category": detected_category,
            "done": True,
            "stream": True,
            "final_text": final_text,
        }
        if room:
            emit_fn("chatbot_response", done_payload, room=room)
        else:
            emit_fn("chatbot_response", done_payload)

        # Save assistant message to memory for context continuity
        if user_email:
            self._add_to_conversation_history(user_email, "assistant", final_text)


    # ======================================================================
    # TOOL DEFINITIONS
    # ======================================================================

    def _get_tools(self) -> List[dict]:
        """
        Define the tools (functions) that the model can call.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_my_upcoming_events",
                    "description": "Get upcoming/registered volunteering events for the current logged-in user (events that haven't happened yet).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
                                "default": 5,
                            }
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_completed_events",
                    "description": "Get completed/past volunteering events that the current logged-in user has registered for and attended. Use this when the user asks about 'completed events', 'past events', 'events I've done', 'history', or 'events I attended'.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of events to return",
                                "default": 50,
                            }
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_events",
                    "description": "Search volunteering events by keyword, location, and date range. Use this for general event discovery (not user-specific). IMPORTANT: For time-based queries like 'this weekend', 'next week', 'today', 'tomorrow', you can use these relative date expressions directly - they will be automatically converted to proper dates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {"type": "string"},
                            "location": {"type": "string"},
                            "start_date": {
                                "type": "string",
                                "description": "Start date in ISO format YYYY-MM-DD, or relative expressions like 'today', 'tomorrow', 'this weekend', 'next weekend', 'this week', 'next week', 'next month'. For 'this weekend', use it as start_date and the system will find events from Saturday onwards. For 'next month', it will expand to the full month range.",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in ISO format YYYY-MM-DD, or relative expressions. For 'this weekend', you can set end_date to 'this weekend' and it will be interpreted as Sunday. For 'next month', it will expand to the last day of next month. For date ranges, always provide both start_date and end_date.",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max events",
                                "default": 10,
                            },
                            "use_semantic": {
                                "type": "boolean",
                                "description": "Whether to use semantic/embedding-based search if available",
                                "default": True,
                            },
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_teams",
                    "description": "Get teams the current user is a member of.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_teams",
                    "description": "List available teams on the platform. If the user is logged in, prefer showing teams they are NOT part of.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_badges",
                    "description": "Get badges earned by the current user.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_available_badges",
                    "description": "List badges the user has NOT earned yet.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_stats",
                    "description": "Get volunteering impact stats (hours, completed events, upcoming events, badges) for the current user.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_team_events",
                    "description": "Get events that the user's teams are registered for.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ]

    # ======================================================================
    # TOOL EXECUTION
    # ======================================================================

    def _execute_tool_call(self, tool_name: str, arguments: dict, user_email: Optional[str]) -> dict:
        """
        Executes the tool by name and returns a dict with:
        {"type": "events|teams|badges|impact|team_events", "data": [...] or {...}}
        """
        # Helper to get user_id
        user_id = None
        if user_email:
            try:
                user_id = self.dao.get_user_id_by_email(user_email)
            except Exception as e:
                print(f"Error getting user_id for {user_email}: {e}")

        # 1) get_my_upcoming_events
        if tool_name == "get_my_upcoming_events":
            if not user_id:
                return {"type": "events", "data": []}
            limit = int(arguments.get("limit", 5))
            events = self.dao.get_upcoming_events(user_id, limit=limit) or []
            normalized = [self._normalize_event(e) for e in events]
            return {"type": "events", "data": normalized}

        # 1b) get_my_completed_events
        if tool_name == "get_my_completed_events":
            if not user_id:
                return {"type": "events", "data": []}
            limit = int(arguments.get("limit", 50))
            events = self.dao.get_completed_events(user_id, limit=limit) or []
            normalized = [self._normalize_event(e) for e in events]
            return {"type": "events", "data": normalized}

        # 2) search_events
        if tool_name == "search_events":
            keyword = arguments.get("keyword")
            location = arguments.get("location")
            start_date_str = arguments.get("start_date")
            end_date_str = arguments.get("end_date")
            
            # Parse dates (handles both ISO format and relative expressions)
            start_date = self._parse_iso_date(start_date_str)
            end_date = self._parse_iso_date(end_date_str)
            
            # Special handling for relative date expressions that need range expansion
            if start_date_str:
                start_lower = start_date_str.lower().strip()
                end_lower = end_date_str.lower().strip() if end_date_str else ""
                today = date.today()
                weekday = today.weekday()
                
                # Handle "this weekend" - expand to Saturday-Sunday range
                if start_lower == "this weekend":
                    days_until_saturday = (5 - weekday) % 7
                    if days_until_saturday == 0 and weekday == 5:
                        saturday = today
                        sunday = today + timedelta(days=1)
                    elif days_until_saturday == 0:
                        saturday = today - timedelta(days=1)
                        sunday = today
                    else:
                        saturday = today + timedelta(days=days_until_saturday)
                        sunday = saturday + timedelta(days=1)
                    
                    if end_lower == "this weekend" or not end_date_str:
                        start_date = saturday
                        end_date = sunday
                    else:
                        start_date = saturday
                
                # Handle "next weekend" - expand to Saturday-Sunday range
                elif start_lower == "next weekend":
                    days_until_next_saturday = (5 - weekday) % 7 + 7
                    saturday = today + timedelta(days=days_until_next_saturday)
                    sunday = saturday + timedelta(days=1)
                    
                    if end_lower == "next weekend" or not end_date_str:
                        start_date = saturday
                        end_date = sunday
                    else:
                        start_date = saturday
                
                # Handle "next week" - expand to Monday-Sunday range
                elif start_lower == "next week":
                    days_until_next_monday = (7 - weekday) % 7
                    if days_until_next_monday == 0:
                        days_until_next_monday = 7
                    monday = today + timedelta(days=days_until_next_monday)
                    sunday = monday + timedelta(days=6)
                    
                    if end_lower == "next week" or not end_date_str:
                        start_date = monday
                        end_date = sunday
                    else:
                        start_date = monday
                
                # Handle "this week" - expand to Monday-Sunday range
                elif start_lower == "this week":
                    days_since_monday = weekday
                    monday = today - timedelta(days=days_since_monday)
                    sunday = monday + timedelta(days=6)
                    
                    if end_lower == "this week" or not end_date_str:
                        start_date = monday
                        end_date = sunday
                    else:
                        start_date = monday
                
                # Handle "next month" - expand to full month range (first day to last day)
                elif start_lower == "next month":
                    if today.month == 12:
                        # December -> January of next year
                        first_day = date(today.year + 1, 1, 1)
                        last_day = date(today.year + 1, 1, calendar.monthrange(today.year + 1, 1)[1])
                    else:
                        first_day = date(today.year, today.month + 1, 1)
                        last_day = date(today.year, today.month + 1, calendar.monthrange(today.year, today.month + 1)[1])
                    
                    if end_lower == "next month" or not end_date_str:
                        start_date = first_day
                        end_date = last_day
                    else:
                        start_date = first_day
            
            limit = int(arguments.get("limit", 10))
            use_semantic = bool(arguments.get("use_semantic", True))

            events: List[dict] = []

            if use_semantic:
                query_text = keyword or ""
                query_embedding = self.embedding_helper.generate_embedding(query_text)
                events = self.dao.search_events_with_embeddings(
                    query_embedding=query_embedding,
                    location=location,
                    limit=limit,
                    similarity_threshold=0.3 if not (start_date or end_date) else 0.05,
                    start_date=start_date,
                    end_date=end_date,
                )
                if not events:
                    events = self.dao.get_filtered_events(
                        keyword=keyword,
                        location=location,
                        start_date=start_date,
                        end_date=end_date,
                    )
            else:
                events = self.dao.get_filtered_events(
                    keyword=keyword,
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                )

            # filter out user's own registered events from recommendations
            if user_email and events:
                try:
                    user_event_ids = self.dao.get_user_events(user_email) or []
                    registered_ids = {
                        (row[0] if isinstance(row, tuple) else row)
                        for row in user_event_ids
                    }
                    filtered = []
                    for ev in events:
                        ev_id = ev.get("ID") or ev.get("id")
                        if ev_id and int(ev_id) in registered_ids:
                            continue
                        filtered.append(ev)
                    events = filtered
                except Exception as e:
                    print(f"Error filtering out user's registered events: {e}")

            events = events[:limit]
            normalized = [self._normalize_event(e) for e in events]
            return {"type": "events", "data": normalized}

        # 3) get_my_teams
        if tool_name == "get_my_teams":
            if not user_email:
                return {"type": "teams", "data": []}
            teams = self.dao.get_all_joined_teams(user_email) or []
            normalized = [self._normalize_team(t, user_id) for t in teams]
            return {"type": "teams", "data": normalized}

        # 4) list_teams
        if tool_name == "list_teams":
            teams = self.dao.get_all_teams() or []
            if user_email:
                try:
                    joined = self.dao.get_all_joined_teams(user_email) or []
                    joined_ids = {
                        int(t.get("ID") or t.get("id"))
                        for t in joined
                        if t.get("ID") or t.get("id")
                    }
                    teams = [
                        t for t in teams
                        if not (t.get("ID") or t.get("id")) or int(t.get("ID") or t.get("id")) not in joined_ids
                    ]
                except Exception as e:
                    print(f"Error filtering joined teams from list_teams: {e}")
            normalized = [self._normalize_team(t, user_id) for t in teams]
            return {"type": "teams", "data": normalized[:10]}

        # 5) get_my_badges
        if tool_name == "get_my_badges":
            if not user_id:
                return {"type": "badges", "data": []}
            user_badges = self.dao.get_user_badges(user_id) or []
            normalized = []
            for b in user_badges:
                bd = dict(b)
                if "ID" in bd and "id" not in bd:
                    bd["id"] = bd["ID"]
                normalized.append(bd)
            return {"type": "badges", "data": normalized}

        # 5b) get_available_badges
        if tool_name == "get_available_badges":
            if not user_id:
                return {"type": "badges", "data": []}
            all_badges = self.dao.get_all_badges() or []
            user_badges = self.dao.get_user_badges(user_id) or []
            user_badge_ids = {
                int(b.get("ID") or b.get("id"))
                for b in user_badges
                if b.get("ID") or b.get("id")
            }
            not_earned = []
            for b in all_badges:
                bid = b.get("ID") or b.get("id")
                if not bid:
                    continue
                if int(bid) not in user_badge_ids:
                    bd = dict(b)
                    if "ID" in bd and "id" not in bd:
                        bd["id"] = bd["ID"]
                    not_earned.append(bd)
            return {"type": "badges", "data": not_earned}

        # 6) get_my_stats
        if tool_name == "get_my_stats":
            if not user_id:
                return {"type": "impact", "data": {}}
            total_hours = self.dao.get_total_hours(user_id)
            completed_events_count = self.dao.get_completed_events_count(user_id)
            upcoming_events_count = self.dao.get_upcoming_events_count(user_id)
            badges_count = len(self.dao.get_badges(user_id))
            stats = {
                "total_hours": total_hours,
                "completed_events": completed_events_count,
                "upcoming_events": upcoming_events_count,
                "badges_count": badges_count,
            }
            return {"type": "impact", "data": stats}

        # 7) get_my_team_events
        if tool_name == "get_my_team_events":
            if not user_email:
                return {"type": "team_events", "data": []}
            team_events = self.dao.get_team_events(user_email) or []
            normalized = [self._normalize_event(e) for e in team_events]
            return {"type": "team_events", "data": normalized}

        # default
        return {"type": "general", "data": []}

    # ======================================================================
    # MEMORY MANAGEMENT (conversation history)
    # ======================================================================

    def _add_to_conversation_history(self, user_email: str, role: str, message: str):
        """Add a message to short-term memory (kept in RAM for context)."""
        if user_email not in self.short_term_memory:
            self.short_term_memory[user_email] = []
        self.short_term_memory[user_email].append({"role": role, "content": message})
        if len(self.short_term_memory[user_email]) > 10:
            self.short_term_memory[user_email] = self.short_term_memory[user_email][-10:]

    def _get_conversation_history(self, user_email: str) -> List[Dict[str, str]]:
        """Retrieve the last few messages for context."""
        if user_email not in self.short_term_memory:
            return []
        return self.short_term_memory[user_email][-10:]

    def _get_user_first_name(self, user_email: str) -> Optional[str]:
        """Fetch and cache the user's first name for personalization."""
        if user_email in self.long_term_memory:
            return self.long_term_memory[user_email]
        try:
            user = self.dao.get_user_by_email(user_email)
            if user and user.get("FirstName"):
                first_name = user["FirstName"]
                self.long_term_memory[user_email] = first_name
                return first_name
        except Exception as e:
            print(f"Error fetching user first name: {e}")
            return None
        return None

    # ======================================================================
    # HELPERS
    # ======================================================================

    def _build_system_prompt(self, user_first_name: Optional[str] = None) -> str:
        if user_first_name:
            personalization_note = (
                f"IMPORTANT: The user's name is {user_first_name}. "
                "Address them by their first name naturally (not in every sentence)."
            )
            return f"{personalization_note}\n\n{SYSTEM_PROMPT}"
        return SYSTEM_PROMPT

    def _parse_relative_date(self, value: Optional[str]) -> Optional[date]:
        """
        Parse relative date expressions like "this weekend", "next week", etc.
        Returns ISO date string (YYYY-MM-DD) or None.
        """
        if not value:
            return None
        
        value_lower = value.lower().strip()
        today = date.today()
        weekday = today.weekday()  # 0=Monday, 6=Sunday
        
        # Handle common relative date expressions
        if value_lower in ["today", "now"]:
            return today
        
        if value_lower == "tomorrow":
            return today + timedelta(days=1)
        
        if value_lower == "this weekend":
            # Find the next Saturday
            days_until_saturday = (5 - weekday) % 7
            if days_until_saturday == 0 and weekday == 5:
                # Today is Saturday, return today
                return today
            elif days_until_saturday == 0:
                # Today is Sunday, return yesterday (Saturday)
                return today - timedelta(days=1)
            else:
                # Return the upcoming Saturday
                return today + timedelta(days=days_until_saturday)
        
        if value_lower == "next weekend":
            # Find Saturday of next week
            days_until_next_saturday = (5 - weekday) % 7 + 7
            return today + timedelta(days=days_until_next_saturday)
        
        if value_lower == "this week":
            # Return Monday of current week
            days_since_monday = weekday
            return today - timedelta(days=days_since_monday)
        
        if value_lower == "next week":
            # Return Monday of next week
            days_until_next_monday = (7 - weekday) % 7
            if days_until_next_monday == 0:
                days_until_next_monday = 7
            return today + timedelta(days=days_until_next_monday)
        
        if value_lower == "next month":
            # Return first day of next month
            if today.month == 12:
                # December -> January of next year
                return date(today.year + 1, 1, 1)
            else:
                return date(today.year, today.month + 1, 1)
        
        # Try parsing as ISO date format
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass
        
        return None
    
    def _parse_iso_date(self, value: Optional[str]) -> Optional[date]:
        """
        Parse date value - first tries relative date parsing, then ISO format.
        """
        if not value:
            return None
        
        # First try relative date parsing
        relative_date = self._parse_relative_date(value)
        if relative_date:
            return relative_date
        
        # Fall back to ISO format parsing
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None

    def _normalize_event(self, event: dict) -> dict:
        """
        Normalize event dictionary keys for frontend compatibility,
        and convert date/time/timedelta to strings so they can be JSON-encoded.
        """
        e = dict(event)

        # map IDs/names
        if "ID" in e and "id" not in e:
            e["id"] = e["ID"]
        if "Title" in e and "title" not in e:
            e["title"] = e["Title"]
        if "LocationCity" in e and "location" not in e:
            e["location"] = e["LocationCity"]
        if "Capacity" in e and "capacity" not in e:
            e["capacity"] = e["Capacity"]

        # convert date/time-like objects to strings
        for key in ["Date", "StartTime", "EndTime", "date", "start_time", "end_time"]:
            if key in e and isinstance(e[key], (date, datetime, timedelta)):
                e[key] = str(e[key])

        return e

    def _normalize_team(self, team: dict, user_id: Optional[int] = None) -> dict:
        """
        Normalize team dictionary keys for frontend compatibility.
        Also determines if the user is the team owner.
        """
        t = dict(team)
        if "ID" in t:
            t["id"] = t["ID"]
        if "Name" in t:
            t["name"] = t["Name"]
        if "JoinCode" in t:
            t["join_code"] = t["JoinCode"]
        if "IsOwner" in t and t["IsOwner"] is not None:
            t["is_owner"] = t["IsOwner"]
        elif user_id and "OwnerUserID" in t:
            t["is_owner"] = t["OwnerUserID"] == user_id
        else:
            t["is_owner"] = False
        return t

    # ======================================================================
    # Legacy helper (kept)
    # ======================================================================
    def get_ai_response(self, prompt: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-nano", messages=[{"role": "user", "content": prompt}]
            )
            if response and response.choices and len(response.choices) > 0:
                msg = response.choices[0].message
                if msg and msg.content:
                    return msg.content.strip()
            return "Sorry, I received an unexpected response from the AI. Please try again."
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "Sorry, I'm having trouble processing your request right now."