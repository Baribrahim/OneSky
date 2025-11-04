"""
Chatbot Connector
Handles chatbot logic for categorizing and responding to user queries.
Supports Events, Teams, Badges, Impact, and General categories.
"""

import os
import re
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from data_access import DataAccess
from .embedding_helper import EmbeddingHelper

load_dotenv()

# Module-level cache for category embeddings (shared across all instances)
_category_embeddings_cache: Dict[str, List[float]] = {}
_category_embeddings_initialized = False

# ---------------------------------------------------------------------
# Shared system prompt (moved out of the method for readability)
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

If the user asks about...
Events:
- If results exist → mention 2–3 relevant events (title, date, time, location), then say: "For more, visit the Events section above."
- If no results → reply briefly, e.g., "No events match that right now — check the Events section for more."
- Support natural, time-based queries (e.g., "this weekend," "next month," "tomorrow").
- If unclear → politely ask for clarification ("Are you looking for upcoming or past events?").

Teams:
- Explain how to create, browse, or join a team.
- Remind users that team creation is done in the Teams section and that join codes are shared by team owners.
- Show query results appropriately.

Badges:
- Explain what badges represent and how to earn them through volunteering activity.
- Tell users they can view earned badges on their Home dashboard.
- Show query results appropriately.

Impact:
- Explain how the user's volunteering hours and events completed contribute to their impact stats, visible on the Home dashboard.
- Show query results appropriately.

General OneSky Queries:
- Briefly explain that OneSky is Sky's internal volunteering platform to help employees find, join, and track volunteer events.
- Mention relevant sections (Home, Events, Teams, Logout) if applicable.

Out-of-Scope Queries:
If the user asks about anything unrelated to OneSky (e.g., Sky corporate info, personal help, or non-volunteering topics, jokes) reply politely:
"I'm sorry, I can only help with volunteering events and features on the OneSky platform."
"""


class ChatbotConnector:
    """
    Main chatbot connector that routes user messages to appropriate handlers
    and generates AI-powered responses.
    """

    # Category example texts for embedding-based classification
    CATEGORY_EXAMPLES = {
        "events": [
            "find volunteer events",
            "give me recommendations for volunteering events",
            "search for volunteer opportunities",
            "what events are available",
            "show me events in my area",
            "find volunteering activities",
            "events near me",
            "upcoming volunteer events",
            "what can I volunteer for",
        ],
        "teams": [
            "what teams are available",
            "how can I join a team",
            "join a team",
            "create a team",
            "team collaboration",
            "group volunteering",
            "how do teams work",
            "join team for volunteering",
            "create volunteer team",
            "what are the upcoming events for my teams",
        ],
        "badges": [
            "what badges do I have",
            "show my achievements",
            "my earned badges",
            "badges I've earned",
            "what achievements can I get",
            "view my badges",
            "how does badges work",
            "what badges are available",
        ],
        "impact": [
            "my hours volunteered",
            "my upcoming events",
            "my completed events",
            "my stats",
            "my progress",
            "how many hours have I volunteered",
            "events I've done",
            "what I've volunteered",
            "my volunteering history",
            "show my impact",
        ],
        "general": [
            "help",
            "what can I do",
            "what can you do",
            "how do I use this",
            "how to navigate",
            "hello",
            "hi",
            "what is this platform",
            "how does this work",
            "what is OneSky",
            "What is this platform",
            "how does this platform work",
        ],
    }

    # ======================================================================
    # Initialization
    # ======================================================================

    def __init__(self):
        """Initialize chatbot connector with data access and OpenAI client."""
        self.dao = DataAccess()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_helper = EmbeddingHelper(api_key)

        # Initialize category embeddings only once (shared across all instances)
        # These embeddings are used to classify user queries into categories
        global _category_embeddings_cache, _category_embeddings_initialized
        if not _category_embeddings_initialized:
            _category_embeddings_cache = self._initialize_category_embeddings()
            _category_embeddings_initialized = True

        # Use the shared cache
        self.category_embeddings = _category_embeddings_cache

    # ======================================================================
    # Main Entry Point
    # ======================================================================

    def process_message(
        self, user_message: str, user_email: Optional[str] = None
    ) -> Tuple[str, str, Optional[List[dict]], Optional[List[dict]], Optional[List[dict]], Optional[List[dict]]]:
        """
        Main entry point - processes user message and returns AI response.
        Returns 6 values consistently:
        (response_text, category, events, teams, badges, team_events)
        """
        # Classify the user's intent into a category (events, teams, badges, impact, general)
        category, message_embedding = self._classify_intent_with_ai(user_message)

        # Route to the appropriate handler based on category
        if category == "events":
            response, events_list = self._handle_events_category(
                user_message, user_email, message_embedding
            )
            return response, category, events_list, None, None, None

        if category == "teams":
            response, teams_list, team_events = self._handle_teams_category(
                user_message, user_email
            )
            return response, category, None, teams_list, None, team_events

        if category == "badges":
            response, badges_list = self._handle_badges_category(
                user_message, user_email
            )
            return response, category, None, None, badges_list, None

        if category == "impact":
            response = self._handle_impact_category(user_message, user_email)
            return response, category, None, None, None, None

        # general
        response = self._handle_general_category(user_message)
        return response, category, None, None, None, None

    # ======================================================================
    # Intent Classification
    # ======================================================================

    def _initialize_category_embeddings(self) -> Dict[str, List[float]]:
        """Generate and cache embeddings for category example texts at startup."""
        category_embeddings: Dict[str, List[float]] = {}
        try:
            # For each category, create an average embedding from all example texts
            # This creates a "representative" embedding for the category
            for category, examples in self.CATEGORY_EXAMPLES.items():
                example_embeddings = []
                for example_text in examples:
                    embedding = self.embedding_helper.generate_embedding(example_text)
                    if embedding:
                        example_embeddings.append(embedding)
                if example_embeddings:
                    # Average all embeddings to get a single category representation
                    avg_embedding = np.mean(example_embeddings, axis=0).tolist()
                    category_embeddings[category] = avg_embedding
        except Exception as e:
            print(f"Error initializing category embeddings: {e}")
        return category_embeddings

    def _match_personal_intent(self, msg: str) -> Optional[str]:
        """
        High-priority rule-based intent detection for 'my ...' style queries.
        This runs before embedding classification to catch personal queries quickly.
        """
        personal_words = ("my", "i ", "i'm", "i am", "me ", "me?")
        is_personal = any(w in msg for w in personal_words)

        # Check for personal team queries
        if "team" in msg and (is_personal or "am i in" in msg or "i'm in" in msg or "belong" in msg):
            return "teams"

        # Check for personal badge queries
        if "badge" in msg or "achievement" in msg:
            if is_personal or "have i earned" in msg or "i earned" in msg or "i've earned" in msg:
                return "badges"

        # Check for personal event queries
        if ("event" in msg or "upcoming" in msg or "coming up" in msg or "attending" in msg) and is_personal:
            return "events"

        return None

    def _classify_intent_with_ai(self, message: str) -> Tuple[str, Optional[List[float]]]:
        """
        Embedding-based classification with a rule-based layer first.
        Uses semantic similarity to match user queries to categories.
        """
        if not message or not message.strip():
            return ("general", None)

        msg = message.lower()

        # Step 1: Quick rule-based check for personal queries (faster than embeddings)
        personal_category = self._match_personal_intent(msg)
        if personal_category:
            return personal_category, None

        # Step 2: Use embedding-based classification for semantic matching
        if not self.category_embeddings:
            # fallback if embeddings were not initialized
            return (self._classify_intent_fallback(message), None)

        try:
            # Generate embedding for the user's message
            message_embedding = self.embedding_helper.generate_embedding(message)
            if not message_embedding:
                return (self._classify_intent_fallback(message), None)

            # Compare user's message embedding with each category embedding
            # Find the category with highest similarity
            best_category = "general"
            best_similarity = -1.0
            for category, category_embedding in self.category_embeddings.items():
                similarity = self.embedding_helper.cosine_similarity(
                    message_embedding, category_embedding
                )
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_category = category

            # If similarity is too low, default to general
            if best_similarity < 0.3:
                return ("general", message_embedding)

            return (best_category, message_embedding)
        except Exception as e:
            print(f"Error in embedding-based classification: {e}")
            return (self._classify_intent_fallback(message), None)

    def _classify_intent_fallback(self, message: str) -> str:
        """Simple keyword-based fallback classifier."""
        if not message or not message.strip():
            return "general"

        message_lower = message.lower()

        personal_indicators = ["my", "i", "me", "mine", "i've", "i have", "i did", "i completed"]
        personal_event_terms = [
            "upcoming",
            "completed",
            "events",
            "event",
            "volunteer",
            "volunteered",
            "hours",
            "stats",
            "statistics",
            "progress",
            "history",
        ]
        has_personal = any(ind in message_lower for ind in personal_indicators)
        has_personal_event = any(term in message_lower for term in personal_event_terms)
        if has_personal and has_personal_event:
            return "impact"

        if any(k in message_lower for k in ["team", "teams", "group", "groups", "collaborate", "join"]):
            return "teams"

        if any(k in message_lower for k in ["badge", "badges", "achievement", "achievements", "award", "awards", "earned"]):
            return "badges"

        if any(k in message_lower for k in ["event", "events", "volunteer", "volunteering", "opportunity", "opportunities", "activity", "activities"]):
            return "events"

        return "general"

    # ======================================================================
    # Category Handlers
    # ======================================================================

    # ---------- EVENTS ----------

    def _handle_events_category(
        self, user_message: str, user_email: Optional[str] = None, query_embedding: Optional[List[float]] = None
    ) -> Tuple[str, List[dict]]:
        """
        Entry for events: decide between personal events vs event search.
        - Personal events: "my upcoming events", "events I'm registered for"
        - Event search: general event discovery and recommendations
        """
        msg_lower = user_message.lower() if user_message else ""
        # Check if user is asking about their own registered events
        is_personal_events = (
            user_email
            and (
                "my" in msg_lower
                or "i'm" in msg_lower
                or "i am" in msg_lower
                or "events i have" in msg_lower
                or "attending" in msg_lower
            )
            and (
                "upcoming" in msg_lower
                or "coming up" in msg_lower
                or "signed up" in msg_lower
                or "registered" in msg_lower
                or "attending" in msg_lower
            )
        )

        if is_personal_events:
            return self._handle_personal_events(user_message, user_email)

        return self._handle_event_search(user_message, user_email, query_embedding)

    def _handle_personal_events(
        self, user_message: str, user_email: str
    ) -> Tuple[str, List[dict]]:
        """
        Handle 'my upcoming events', 'what events do I have coming up', etc.
        Fetches the user's registered upcoming events from the database.
        """
        user_events: List[dict] = []
        user_id = self.dao.get_user_id_by_email(user_email)

        # Try to get upcoming events using user_id (preferred method)
        if user_id:
            try:
                user_events = self.dao.get_upcoming_events(user_id, limit=5) or []
            except Exception as e:
                print(f"Error getting upcoming events for user {user_id}: {e}")
                user_events = []

        # Fallback: if that didn't work, try getting events by email
        # Some database setups may return event IDs that need to be resolved
        if not user_events and user_email:
            try:
                registered = self.dao.get_user_events(user_email) or []
                full_events = []
                for item in registered:
                    event_id = item[0] if isinstance(item, tuple) else item
                    if not event_id:
                        continue
                    if hasattr(self.dao, "get_event_by_id"):
                        ev = self.dao.get_event_by_id(event_id)
                        if ev:
                            full_events.append(ev)
                if full_events:
                    user_events = full_events
            except Exception as e:
                print(f"Error falling back to user_events for {user_email}: {e}")

        formatted_user_events = (
            self._format_events_for_context(user_events) if user_events else "No upcoming events"
        )
        prompt = f"""{self._build_system_prompt()}

User's question: {user_message}

User's upcoming/registered events:
{formatted_user_events}

CRITICAL - Response Formatting:
- Events will be displayed as interactive cards below your message, so DO NOT mention specific event details (title, date, time, location) in your text response
- Keep it to 1–2 sentences, friendly.
"""
        response_text = self.get_ai_response(prompt)

        events_list = [self._normalize_event(e) for e in user_events]
        return response_text, events_list

    def _handle_event_search(
        self,
        user_message: str,
        user_email: Optional[str],
        query_embedding: Optional[List[float]],
    ) -> Tuple[str, List[dict]]:
        """
        Handle normal event search / recommendations.
        Uses embedding-based search if available, otherwise falls back to keyword search.
        Filters out events the user is already registered for.
        """
        location = self._extract_location(user_message)
        wants_single_event = self._detect_single_event_request(user_message)

        # Generate embedding if not provided (reuses embedding from classification when possible)
        if not query_embedding:
            query_embedding = self.embedding_helper.generate_embedding(user_message)

        # Use embedding-based search if available, otherwise keyword search
        if not query_embedding:
            message_for_keywords = (
                self._remove_location_from_message(user_message, location)
                if location
                else user_message
            )
            keyword = self._extract_keyword(message_for_keywords)
            events = self.dao.get_filtered_events(keyword, location, None, None)
        else:
            # Semantic search using embeddings (better for understanding intent)
            events = self.dao.search_events_with_embeddings(
                query_embedding=query_embedding,
                location=location,
                limit=10,
                similarity_threshold=0.3,
            )

        # Filter out events user is already registered for (for recommendations)
        if user_email and events:
            try:
                user_registered_events = self.dao.get_user_events(user_email)
                registered_event_ids = set()
                if user_registered_events:
                    for event_tuple in user_registered_events:
                        event_id = event_tuple[0] if isinstance(event_tuple, tuple) else event_tuple
                        if event_id:
                            registered_event_ids.add(int(event_id))

                filtered_events = []
                for event in events:
                    event_id = event.get("ID") or event.get("id")
                    if event_id and int(event_id) in registered_event_ids:
                        continue
                    filtered_events.append(event)
                events = filtered_events
            except Exception as e:
                print(f"Error filtering user's registered events: {e}")

        formatted_events = self._format_events_for_context(events)
        prompt = f"""{self._build_system_prompt()}

User's question: {user_message}

Available events from database ({len(events)} found):
{formatted_events}

IMPORTANT - Event Registration Process:
When users ask to "sign up", "register", or "join" an event, they mean registering for a volunteer event:
1. Go to the Events page via the header menu
2. Find the event you want
3. Click Register (or Volunteer)
4. The event will appear in your upcoming events on the home dashboard

CRITICAL - Response Formatting:
- Events will be displayed as interactive cards below your message, so DO NOT mention specific event details
- Keep your response CONCISE - just 1-2 sentences maximum
- Be friendly and brief
"""
        response_text = self.get_ai_response(prompt)

        events_list: List[dict] = []
        if events:
            limit = 1 if wants_single_event else 3
            for event in events[:limit]:
                events_list.append(self._normalize_event(event))

        return response_text, events_list

    # ---------- TEAMS ----------

    def _handle_teams_category(
        self, user_message: str, user_email: Optional[str] = None
    ) -> Tuple[str, List[dict], List[dict]]:
        """
        Handle Teams category - team-related queries.
        Returns: (response_text, teams_list, team_events_list)
        """
        user_teams: List[dict] = []
        all_teams: List[dict] = []
        team_events: List[dict] = []

        # Fetch team data for logged-in users
        if user_email:
            try:
                user_teams = self.dao.get_all_joined_teams(user_email)
                all_teams = self.dao.get_all_teams()
                team_events = self.dao.get_team_events(user_email)
            except Exception as e:
                print(f"Error fetching team data: {e}")

        # Fast path: if user is asking about "my teams", return their teams directly
        if self._is_asking_about_my_teams(user_message):
            prompt = f"""{self._build_system_prompt()}

User's question: {user_message}

User's teams ({len(user_teams)}):
{self._format_teams_for_context(user_teams)}

CRITICAL - Response Formatting:
- Teams will be displayed as interactive cards below your message, so DO NOT mention specific team details
- Keep it to 1–2 sentences.
"""
            response_text = self.get_ai_response(prompt)

            user_id = self.dao.get_user_id_by_email(user_email) if user_email else None
            teams_list = [self._normalize_team(t, user_id) for t in user_teams]
            return response_text, teams_list, team_events

        # generic path
        wants_all_teams = self._detect_all_teams_request(user_message)
        wants_single_team = self._detect_single_team_request(user_message)
        matching_team_by_name = self._find_matching_team(user_message, all_teams)

        teams_to_return: List[dict] = []
        if wants_all_teams:
            teams_to_return = all_teams[:10] if all_teams else []
        elif matching_team_by_name:
            if user_email and user_teams:
                joined_ids = {int(t.get("ID") or t.get("id")) for t in user_teams if t.get("ID") or t.get("id")}
                mt_id = matching_team_by_name.get("ID") or matching_team_by_name.get("id")
                if mt_id and int(mt_id) not in joined_ids:
                    teams_to_return = [matching_team_by_name]
            else:
                teams_to_return = [matching_team_by_name]
        elif wants_single_team:
            teams_to_return = all_teams[:1] if all_teams else []
        else:
            teams_to_return = all_teams[:3] if all_teams else []

        # filter out teams user is already in (for generic list)
        if user_email and user_teams and teams_to_return:
            try:
                joined_ids = {int(t.get("ID") or t.get("id")) for t in user_teams if t.get("ID") or t.get("id")}
                teams_to_return = [
                    t for t in teams_to_return
                    if not (t.get("ID") or t.get("id")) or int(t.get("ID") or t.get("id")) not in joined_ids
                ]
            except Exception as e:
                print(f"Error filtering user's joined teams: {e}")

        prompt = f"""{self._build_system_prompt()}

User's question: {user_message}

IMPORTANT - Team Instructions:

**Joining a Team:**
Go to Teams in the header menu, browse available teams, and join using a join code.

**Creating a Team:**
Go to Teams in the header menu, click on "Create Team" in the My Teams section, fill in the details (name, description, department, capacity), click Create, and share the join code with others so they can join.

**Registering as a Team for an Event:**
The team owner can go to Events in the header menu, find an event, click on "Register as a Team" to register the team to that event.

User's teams ({len(user_teams)}):
{self._format_teams_for_context(user_teams)}

Available teams (showing first 10):
{self._format_teams_for_context(all_teams[:10]) if all_teams else "No teams available"}

Events your teams are registered for:
{self._format_events_for_context(team_events) if team_events else "No team events"}

CRITICAL - Response Formatting:
- Teams will be displayed as interactive cards below your message, so DO NOT mention specific team details in your text response
- Keep your response CONCISE - just 1-2 sentences maximum
- Be friendly and brief
"""
        response_text = self.get_ai_response(prompt)

        user_id = self.dao.get_user_id_by_email(user_email) if user_email else None
        teams_list = [self._normalize_team(t, user_id) for t in teams_to_return]
        return response_text, teams_list, team_events

    # ---------- BADGES ----------

    def _handle_badges_category(
        self, user_message: str, user_email: Optional[str] = None
    ) -> Tuple[str, List[dict]]:
        """Handle Badges category - user badges and achievements."""
        if not user_email:
            return "Please log in to view your badges and achievements.", None

        user_id = self.dao.get_user_id_by_email(user_email)
        if not user_id:
            return "Unable to retrieve your account information. Please try again.", None

        user_badges = self.dao.get_badges(user_id)
        all_badges = self.dao.get_all_badges()

        is_asking_about_my_badges = self._is_asking_about_my_badges(user_message)
        is_asking_about_all_badges = (not is_asking_about_my_badges) and self._is_asking_about_all_badges(user_message)

        if is_asking_about_my_badges:
            badges_to_return = user_badges[:5] if user_badges else []
        elif is_asking_about_all_badges:
            user_badge_ids = {int(b.get("ID") or b.get("id")) for b in user_badges if (b.get("ID") or b.get("id"))}
            available_badges = [
                b for b in all_badges
                if (b.get("ID") or b.get("id")) and int(b.get("ID") or b.get("id")) not in user_badge_ids
            ]
            badges_to_return = available_badges[:2] if available_badges else []
        else:
            badges_to_return = user_badges[:3] if user_badges else all_badges[:2]

        prompt = f"""{self._build_system_prompt()}

User's question: {user_message}

User's earned badges ({len(user_badges)} total):
{self._format_badges_for_context(user_badges)}

All available badges:
{self._format_all_badges_for_context(all_badges)}

CRITICAL - Response Formatting:
- Badges will be displayed as interactive cards below your message, so DO NOT mention specific badge details
- Keep your response CONCISE - just 1-2 sentences maximum
"""
        response_text = self.get_ai_response(prompt)

        badges_list = []
        for badge in badges_to_return:
            badge_dict = dict(badge)
            if "ID" in badge_dict and "id" not in badge_dict:
                badge_dict["id"] = badge_dict["ID"]
            badges_list.append(badge_dict)

        return response_text, badges_list

    # ---------- IMPACT ----------

    def _handle_impact_category(self, user_message: str, user_email: Optional[str] = None) -> str:
        """Handle Impact category - user statistics and progress."""
        if not user_email:
            return "Please log in to view your volunteering impact."

        user_id = self.dao.get_user_id_by_email(user_email)
        if not user_id:
            return "Unable to retrieve your account information. Please try again."

        total_hours = self.dao.get_total_hours(user_id)
        completed_events_count = self.dao.get_completed_events_count(user_id)
        upcoming_events_count = self.dao.get_upcoming_events_count(user_id)
        badges_count = len(self.dao.get_badges(user_id))

        upcoming_events_list = self.dao.get_upcoming_events(user_id, limit=5)
        completed_events_list = self.dao.get_completed_events(user_id, limit=5)

        prompt = f"""{self._build_system_prompt()}

User's question: {user_message}

User's volunteering impact:
- Total hours volunteered: {total_hours:.1f} hours
- Events completed: {completed_events_count}
- Upcoming events: {upcoming_events_count}
- Badges earned: {badges_count}

Upcoming events (next 5):
{self._format_events_for_context(upcoming_events_list) if upcoming_events_list else "No upcoming events"}

Recently completed events (last 5):
{self._format_events_for_context(completed_events_list) if completed_events_list else "No completed events yet"}

NOTE: Only show stats, no events, teams or anything else.
"""
        return self.get_ai_response(prompt)

    # ---------- GENERAL ----------

    def _handle_general_category(self, user_message: str) -> str:
        prompt = f"""{self._build_system_prompt()}

User's question: {user_message}"""
        return self.get_ai_response(prompt)

    # ======================================================================
    # Text Processing & Extraction
    # ======================================================================

    def _extract_keyword(self, message: str) -> Optional[str]:
        if not message or not message.strip():
            return None

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "from",
            "what",
            "where",
            "when",
            "show",
            "me",
            "find",
            "search",
            "get",
            "list",
            "available",
            "events",
            "event",
            "are",
            "is",
            "am",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "can",
            "could",
            "would",
            "should",
            "will",
            "this",
            "that",
            "these",
            "those",
        }

        words = message.lower().strip().split()
        keywords = [w.strip() for w in words if w not in stop_words and len(w.strip()) > 2]
        keywords = [w for w in keywords if w and (w.isalnum() or any(c.isalpha() for c in w))]
        if not keywords:
            return None
        return " ".join(keywords[:3])

    def _extract_location(self, message: str) -> Optional[str]:
        locations = self.dao.get_location()
        if not locations:
            return None

        message_lower = message.lower()
        for city in sorted(locations, key=len, reverse=True):
            if not city:
                continue
            if city.lower().strip() in message_lower:
                return city
        return None

    def _remove_location_from_message(self, message: str, location: str) -> str:
        if not location:
            return message
        location_patterns = [
            r"\b" + re.escape(location.lower()) + r"\b",
            r"\bin\s+" + re.escape(location.lower()) + r"\b",
            r"\b" + re.escape(location.lower()) + r"\s+events?\b",
            r"\bevents?\s+(?:in\s+)?"
            + re.escape(location.lower())
            + r"\b",
        ]
        result = message
        for pattern in location_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        return " ".join(result.split())

    def _detect_single_event_request(self, message: str) -> bool:
        if not message:
            return False
        message_lower = message.lower()
        single_event_patterns = [
            r"\b(a|an)\s+(event|volunteer|opportunity|activity)",
            r"\bone\s+(event|volunteer|opportunity|activity)",
            r"\b(a|an)\s+volunteering",
            r"\bone\s+volunteering",
            r"\bshow\s+me\s+(a|an|one)",
            r"\bfind\s+me\s+(a|an|one)",
            r"\bgive\s+me\s+(a|an|one)",
            r"\bsuggest\s+(a|an|one)",
            r"\brecommend\s+(a|an|one)",
        ]
        return any(re.search(p, message_lower) for p in single_event_patterns)

    def _detect_all_teams_request(self, message: str) -> bool:
        if not message:
            return False
        msg = message.lower()
        patterns = [
            r"\ball\s+teams",
            r"\bevery\s+team",
            r"\bshow\s+(all|every)\s+teams",
            r"\blist\s+(all|every)\s+teams",
            r"\bbrowse\s+(all|every)\s+teams",
            r"\bwhat\s+teams\s+(are\s+there|exist|available)",
        ]
        return any(re.search(p, msg) for p in patterns)

    def _detect_single_team_request(self, message: str) -> bool:
        if not message:
            return False
        msg = message.lower()
        patterns = [
            r"\b(a|an)\s+team",
            r"\bone\s+team",
            r"\bshow\s+me\s+(a|an|one)\s+team",
            r"\bfind\s+me\s+(a|an|one)\s+team",
            r"\bgive\s+me\s+(a|an|one)\s+team",
        ]
        return any(re.search(p, msg) for p in patterns)

    def _is_asking_about_my_teams(self, message: str) -> bool:
        if not message:
            return False
        msg = message.lower()
        patterns = [
            r"\bmy\s+teams",
            r"\bteams\s+i\s+(am\s+in|joined|belong\s+to)",
            r"\bteams\s+i'm\s+in",
            r"\bwhat\s+teams\s+(am\s+i|do\s+i\s+have|am\s+i\s+part\s+of)",
        ]
        return any(re.search(p, msg) for p in patterns)

    def _find_matching_team(self, message: str, all_teams: List[dict]) -> Optional[dict]:
        if not all_teams:
            return None
        msg = message.lower().strip()
        query_words = [
            "team",
            "teams",
            "show",
            "find",
            "get",
            "tell",
            "me",
            "about",
            "the",
            "a",
            "an",
            "is",
            "are",
            "what",
            "which",
            "who",
            "how",
        ]
        words = [w for w in msg.split() if w not in query_words and len(w) > 2]
        potential_team_name = " ".join(words).strip()

        best_match = None
        best_score = 0
        for team in all_teams:
            team_name = (team.get("Name") or team.get("name") or "").strip()
            if not team_name:
                continue
            t = team_name.lower()
            score = 0
            if t == msg or t == potential_team_name:
                score = 100
            elif re.search(r"\b" + re.escape(t) + r"\b", msg):
                score = 80
            elif all(w in t for w in words if len(w) > 2):
                score = 60
            elif t in msg:
                score = 50
            elif any(w in t for w in words if len(w) > 2):
                score = 40
            if score > best_score:
                best_score = score
                best_match = team

        return best_match if best_score >= 40 else None

    def _is_asking_about_my_badges(self, message: str) -> bool:
        if not message:
            return False
        msg = message.lower()
        patterns = [
            r"\bmy\s+badges",
            r"\bbadges\s+i\s+(have|earned|got|own)",
            r"\bbadges\s+i've\s+(earned|got)",
            r"\bwhat\s+badges\s+(do\s+i\s+have|have\s+i\s+earned|am\s+i\s+part\s+of)",
            r"\bshow\s+my\s+badges",
        ]
        return any(re.search(p, msg) for p in patterns)

    def _is_asking_about_all_badges(self, message: str) -> bool:
        if not message:
            return False
        msg = message.lower()
        earn_words = [
            "available",
            "can earn",
            "to earn",
            "work towards",
            "other badges",
            "what badges can i",
            "missing",
            "haven't earned",
            "havent earned",
            "haven’t got",
            "can i earn",
            "can i still earn",
            "available badges",
            "what can i still unlock",
            "badges i don’t have",
            "badges i dont have",
        ]
        return any(w in msg for w in earn_words)

    # ======================================================================
    # Data Formatting / Normalisation
    # ======================================================================

    def _normalize_event(self, event: dict) -> dict:
        """
        Normalize event dictionary keys for frontend compatibility.
        Converts database field names (ID, Title) to frontend-friendly names (id, title).
        """
        e = dict(event)
        if "ID" in e and "id" not in e:
            e["id"] = e["ID"]
        if "Title" in e and "title" not in e:
            e["title"] = e["Title"]
        if "LocationCity" in e and "location" not in e:
            e["location"] = e["LocationCity"]
        if "Capacity" in e and "capacity" not in e:
            e["capacity"] = e["Capacity"]
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

    def _format_events_for_context(self, events: List[dict]) -> str:
        if not events:
            return "No events found matching your criteria."
        formatted = []
        for event in events[:10]:
            event_str = f"Event ID {event['ID']}: {event['Title']}"
            if event.get("Date"):
                event_str += f" - Date: {event['Date']}"
            if event.get("StartTime") and event.get("EndTime"):
                event_str += f" - Time: {event['StartTime']} to {event['EndTime']}"
            elif event.get("StartTime"):
                event_str += f" - Time: {event['StartTime']}"
            location_parts = []
            if event.get("LocationCity"):
                location_parts.append(event["LocationCity"])
            if event.get("Address"):
                location_parts.append(event["Address"])
            if location_parts:
                event_str += f" - Location: {', '.join(location_parts)}"
            if event.get("DurationHours"):
                event_str += f" - Duration: {event['DurationHours']:.1f} hours"
            if event.get("About"):
                event_str += f" - About: {event['About'][:150]}"
            formatted.append(event_str)
        return "\n".join(formatted)

    def _format_badges_for_context(self, badges: List[dict]) -> str:
        if not badges:
            return "No badges earned yet."
        return "\n".join(f"- {b['Name']}: {b['Description']}" for b in badges)

    def _format_all_badges_for_context(self, badges: List[dict]) -> str:
        if not badges:
            return "No badges available."
        return "\n".join(f"- {b['Name']}: {b['Description']}" for b in badges[:20])

    def _format_teams_for_context(self, teams: List[dict]) -> str:
        if not teams:
            return "No teams found."
        formatted = []
        for team in teams[:10]:
            s = f"Team ID {team['ID']}: {team.get('Name', 'Unnamed Team')}"
            if team.get("Description"):
                s += f" - {team['Description'][:100]}"
            if team.get("Department"):
                s += f" - Department: {team['Department']}"
            formatted.append(s)
        return "\n".join(formatted)

    # ======================================================================
    # Prompt builder / AI
    # ======================================================================

    def _build_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def get_ai_response(self, prompt: str) -> str:
        """
        Generate AI response using OpenAI API.
        Takes a formatted prompt and returns the AI's text response.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5-nano", messages=[{"role": "user", "content": prompt}]
            )
            if response and response.choices and len(response.choices) > 0:
                msg = response.choices[0].message
                if msg and msg.content:
                    return msg.content.strip()
            return "Sorry, I received an unexpected response from the AI. Please try again."
        except Exception as e:
            print(f"OpenAI API error: {e}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
            return f"Sorry, I'm having trouble processing your request right now. Error: {str(e)[:100]}"
