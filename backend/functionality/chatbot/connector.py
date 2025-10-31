"""
Chatbot Connector
Handles chatbot logic for categorizing and responding to user queries.
Supports Events, Teams, Badges, Impact, and General categories.
"""
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from data_access import DataAccess
from .embedding_helper import EmbeddingHelper

load_dotenv()


class ChatbotConnector:
    """
    Main chatbot connector that routes user messages to appropriate handlers
    and generates AI-powered responses.
    """
    
    # ============================================================================
    # Initialization
    # ============================================================================
    
    def __init__(self):
        """Initialize chatbot connector with data access and OpenAI client."""
        self.dao = DataAccess()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.openai_client = OpenAI(api_key=api_key)
        self.embedding_helper = EmbeddingHelper(api_key)
    
    # ============================================================================
    # Main Entry Point
    # ============================================================================
    
    def process_message(self, user_message, user_email=None):
        """
        Main entry point - processes user message and returns AI response.
        Routes to appropriate category handler based on intent classification.
        
        Args:
            user_message (str): User's message/query
            user_email (str, optional): User's email for personalized responses
            
        Returns:
            tuple: (response_text, category) - AI response and detected category
        """
        category = self._classify_intent_with_ai(user_message)
        
        # Route to appropriate category handler
        if category == "events":
            response = self._handle_events_category(user_message, user_email)
        elif category == "teams":
            response = self._handle_teams_category(user_message, user_email)
        elif category == "badges":
            response = self._handle_badges_category(user_message, user_email)
        elif category == "impact":
            response = self._handle_impact_category(user_message, user_email)
        else:  # general
            response = self._handle_general_category(user_message)
        
        return response, category
    
    # ============================================================================
    # Intent Classification
    # ============================================================================
    
    def _classify_intent_with_ai(self, message):
        """
        Use AI reasoning to classify user intent into one of 5 categories.
        
        Args:
            message (str): User message
            
        Returns:
            str: One of "events", "teams", "badges", "impact", or "general"
        """
        if not message or not message.strip():
            return "general"
        
        try:
            classification_prompt = f"""You are an intent classifier for a volunteering platform chatbot called OneSky.

User message: "{message}"

Classify this message into ONE of these categories:

1. "events" - Asking about finding/searching volunteer events, activities, opportunities to participate in (general search/discovery)
2. "teams" - Asking about joining/creating teams, team collaboration, group volunteering
3. "badges" - Asking about achievements, badges earned, awards, accomplishments
4. "impact" - Asking about PERSONAL statistics, MY hours volunteered, MY progress, MY completed events, MY upcoming events, MY volunteering history. Uses words like "my", "I", "me", "my upcoming", "my completed", "events I've done", "what I've volunteered"
5. "general" - General questions, platform help, navigation, greetings, or unclear intent

IMPORTANT: If the message asks about "my upcoming events", "my completed events", "events I've done", "what I've volunteered", "my progress", "my stats", "my hours" - classify as "impact".

Respond with ONLY the category name (lowercase): events, teams, badges, impact, or general"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-5-nano",
                messages=[{"role": "user", "content": classification_prompt}]
            )
            
            if response and response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content.strip().lower()
                
                # Validate and return category
                valid_categories = ["events", "teams", "badges", "impact", "general"]
                for category in valid_categories:
                    if category in content:
                        return category
                
                return "general"
            
            return "general"
        except Exception as e:
            print(f"Error in AI intent classification: {e}")
            return self._classify_intent_fallback(message)
    
    def _classify_intent_fallback(self, message):
        """
        Fallback keyword-based classification if AI fails.
        Checks for personal context first, then general keywords.
        
        Args:
            message (str): User message
            
        Returns:
            str: Detected category
        """
        if not message or not message.strip():
            return "general"
        
        message_lower = message.lower()
        
        # Check for personal queries first (impact category)
        personal_indicators = ["my", "i", "me", "mine", "i've", "i have", "i did", "i completed"]
        personal_event_terms = ["upcoming", "completed", "events", "event", "volunteer", "volunteered", 
                               "hours", "stats", "statistics", "progress", "history"]
        
        has_personal = any(indicator in message_lower for indicator in personal_indicators)
        has_personal_event_term = any(term in message_lower for term in personal_event_terms)
        
        if has_personal and has_personal_event_term:
            return "impact"
        
        # Standalone impact keywords
        standalone_impact_keywords = ["impact", "my hours", "my stats", "my progress", "my badges", "my achievements"]
        if any(keyword in message_lower for keyword in standalone_impact_keywords):
            return "impact"
        
        # Other categories
        teams_keywords = ["team", "teams", "group", "groups", "collaborate", "join"]
        if any(keyword in message_lower for keyword in teams_keywords):
            return "teams"
        
        badges_keywords = ["badge", "badges", "achievement", "achievements", "award", "awards", "earned"]
        if any(keyword in message_lower for keyword in badges_keywords):
            return "badges"
        
        events_keywords = ["event", "events", "volunteer", "volunteering", "opportunity", 
                          "opportunities", "activity", "activities"]
        if any(keyword in message_lower for keyword in events_keywords):
            return "events"
        
        return "general"
    
    # ============================================================================
    # Category Handlers
    # ============================================================================
    
    def _handle_events_category(self, user_message, user_email=None):
        """Handle Events category - find and search volunteer events."""
        location = self._extract_location(user_message)
        query_embedding = self.embedding_helper.generate_embedding(user_message)
        
        if not query_embedding:
            # Fallback to keyword search
            message_for_keywords = self._remove_location_from_message(user_message, location) if location else user_message
            keyword = self._extract_keyword(message_for_keywords)
            events = self.dao.get_filtered_events(keyword, location, None, None)
        else:
            # Use embedding-based search
            events = self.dao.search_events_with_embeddings(
                query_embedding=query_embedding,
                location=location,
                limit=10,
                similarity_threshold=0.3
            )
        
        formatted_events = self._format_events_for_context(events)
        prompt = self._build_events_prompt(user_message, formatted_events, len(events))
        return self.get_ai_response(prompt)
    
    def _handle_teams_category(self, user_message, user_email=None):
        """Handle Teams category - team-related queries."""
        prompt = f"""You are a helpful assistant for OneSky, a volunteering platform.

User's question: {user_message}

OneSky supports team collaboration for group volunteering.

Instructions:
- Keep your response CONCISE - 1-2 short paragraphs maximum
- Directly answer what the user is asking about teams
- Only provide information relevant to their specific question
- Use emojis sparingly (👥 🤝) - only if helpful
- Be friendly but brief - no lengthy explanations
- If they ask "what is teams" - briefly explain in 2 sentences
- If they ask "how to join" - briefly explain in 2 sentences
- Don't provide information they didn't ask for"""
        
        return self.get_ai_response(prompt)
    
    def _handle_badges_category(self, user_message, user_email=None):
        """Handle Badges category - user badges and achievements."""
        if not user_email:
            return "Please log in to view your badges and achievements."
        
        user_id = self.dao.get_user_id_by_email(user_email)
        if not user_id:
            return "Unable to retrieve your account information. Please try again."
        
        user_badges = self.dao.get_badges(user_id)
        all_badges = self.dao.get_all_badges()
        
        formatted_user_badges = self._format_badges_for_context(user_badges)
        formatted_all_badges = self._format_all_badges_for_context(all_badges)
        
        prompt = f"""You are a helpful assistant for OneSky, a volunteering platform.

User's question: {user_message}

User's earned badges ({len(user_badges)} total):
{formatted_user_badges}

All available badges:
{formatted_all_badges}

Instructions:
- Keep your response CONCISE - 1-2 short paragraphs maximum
- Directly answer the user's question about badges
- If they have badges: briefly mention what they've earned (1-2 sentences)
- If they ask "what badges can I get": briefly mention 1-2 relevant available badges
- Only provide information directly relevant to their question
- Use emojis sparingly (🏆 🎯) - only if helpful
- Be encouraging but brief - no lengthy celebrations or suggestions unless asked"""
        
        return self.get_ai_response(prompt)
    
    def _handle_impact_category(self, user_message, user_email=None):
        """Handle Impact category - user statistics and progress."""
        if not user_email:
            return "Please log in to view your volunteering impact."
        
        user_id = self.dao.get_user_id_by_email(user_email)
        if not user_id:
            return "Unable to retrieve your account information. Please try again."
        
        # Get user statistics
        total_hours = self.dao.get_total_hours(user_id)
        completed_events_count = self.dao.get_completed_events_count(user_id)
        upcoming_events_count = self.dao.get_upcoming_events_count(user_id)
        badges_count = len(self.dao.get_badges(user_id))
        
        # Get actual events data
        upcoming_events_list = self.dao.get_upcoming_events(user_id, limit=5)
        completed_events_list = self.dao.get_completed_events(user_id, limit=5)
        
        formatted_upcoming = self._format_events_for_context(upcoming_events_list) if upcoming_events_list else "No upcoming events"
        formatted_completed = self._format_events_for_context(completed_events_list) if completed_events_list else "No completed events yet"
        
        prompt = f"""You are a helpful assistant for OneSky, a volunteering platform.

User's question: {user_message}

User's volunteering impact:
- Total hours volunteered: {total_hours:.1f} hours
- Events completed: {completed_events_count}
- Upcoming events: {upcoming_events_count}
- Badges earned: {badges_count}

Upcoming events (next 5):
{formatted_upcoming}

Recently completed events (last 5):
{formatted_completed}

Instructions:
- Keep your response CONCISE - 2-3 short paragraphs maximum
- Directly answer what the user is asking about their impact
- If they ask about stats: briefly provide the key numbers (1 paragraph)
- If they ask about upcoming events: briefly mention 1-2 upcoming events with dates (1 paragraph)
- If they ask about completed events: briefly mention 1-2 recent events (1 paragraph)
- Only include information relevant to their specific question
- Use emojis sparingly (📊 ⏱️ ✅ 📅) - only if helpful
- Be encouraging but brief - no lengthy celebrations or motivational speeches"""
        
        return self.get_ai_response(prompt)
    
    def _handle_general_category(self, user_message):
        """Handle General category - platform help, navigation, greetings."""
        prompt = f"""You are a helpful assistant for OneSky, a volunteering platform.

User's question: {user_message}

OneSky is a volunteering platform where users can find events, track impact, earn badges, and join teams.
All navigation and features can be accessed from the header menu at the top of the page.

Instructions:
- Keep your response CONCISE - 1-2 short paragraphs maximum
- Directly answer the user's question or greeting
- If it's a greeting: briefly welcome them and suggest exploring events (2 sentences)
- If they ask for help, guidance, or navigation: direct them to the header menu where all features can be accessed
- If they ask "what can I do": briefly mention main features and direct them to the header (2-3 sentences)
- If they ask "where can I find X": tell them it's in the header menu and which section (e.g., "Home", "Events", "Teams")
- Emphasize that everything can be accessed from the header navigation
- Only provide information relevant to their specific question
- Use emojis sparingly (🌟 🎯) - only if helpful
- Be helpful but brief - no lengthy explanations of all features"""
        
        return self.get_ai_response(prompt)
    
    # ============================================================================
    # Text Processing & Extraction
    # ============================================================================
    
    def _extract_keyword(self, message):
        """
        Extract search keywords from user message.
        
        Args:
            message (str): User message
            
        Returns:
            str or None: Extracted keywords (up to 3), or None if no meaningful keywords
        """
        if not message or not message.strip():
            return None
        
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", 
            "from", "what", "where", "when", "show", "me", "find", "search", "get", "list", 
            "available", "events", "event", "are", "is", "am", "have", "has", "had", "do", 
            "does", "did", "can", "could", "would", "should", "will", "this", "that", "these", "those"
        }
        
        words = message.lower().strip().split()
        keywords = [w.strip() for w in words if w not in stop_words and len(w.strip()) > 2]
        keywords = [w for w in keywords if w and (w.isalnum() or any(c.isalpha() for c in w))]
        
        if not keywords:
            return None
        
        result = " ".join(keywords[:3])
        return result if result.strip() else None
    
    def _extract_location(self, message):
        """
        Extract location from message by matching against known cities.
        
        Args:
            message (str): User message
            
        Returns:
            str or None: Matched city name, or None if not found
        """
        locations = self.dao.get_location()
        if not locations:
            return None
        
        message_lower = message.lower()
        sorted_locations = sorted(locations, key=len, reverse=True)
        
        for city in sorted_locations:
            if not city:
                continue
            city_lower = city.lower().strip()
            if city_lower and city_lower in message_lower:
                return city
        
        return None
    
    def _remove_location_from_message(self, message, location):
        """
        Remove location from message in various patterns (case-insensitive).
        
        Args:
            message (str): User message
            location (str): Location to remove
            
        Returns:
            str: Message with location removed
        """
        if not location:
            return message
        
        location_patterns = [
            r'\b' + re.escape(location.lower()) + r'\b',
            r'\bin\s+' + re.escape(location.lower()) + r'\b',
            r'\b' + re.escape(location.lower()) + r'\s+events?\b',
            r'\bevents?\s+(?:in\s+)?' + re.escape(location.lower()) + r'\b',
        ]
        
        result = message
        for pattern in location_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        return ' '.join(result.split())
    
    # ============================================================================
    # Data Formatting
    # ============================================================================
    
    def _format_events_for_context(self, events):
        """
        Format events data into readable context for AI.
        Handles various event formats (search results, user events, etc.).
        
        Args:
            events (list): List of event dictionaries
            
        Returns:
            str: Formatted event context string
        """
        if not events:
            return "No events found matching your criteria."
        
        formatted = []
        for event in events[:10]:
            event_str = f"Event ID {event['ID']}: {event['Title']}"
            
            # Date and time
            if event.get('Date'):
                event_str += f" - Date: {event['Date']}"
            if event.get('StartTime') and event.get('EndTime'):
                event_str += f" - Time: {event['StartTime']} to {event['EndTime']}"
            elif event.get('StartTime'):
                event_str += f" - Time: {event['StartTime']}"
            
            # Location
            location_parts = []
            if event.get('LocationCity'):
                location_parts.append(event['LocationCity'])
            if event.get('Address'):
                location_parts.append(event['Address'])
            if location_parts:
                event_str += f" - Location: {', '.join(location_parts)}"
            
            # Duration (for completed events)
            if event.get('DurationHours'):
                event_str += f" - Duration: {event['DurationHours']:.1f} hours"
            
            # Description
            if event.get('About'):
                event_str += f" - About: {event['About'][:150]}"
            
            formatted.append(event_str)
        
        return "\n".join(formatted)
    
    def _format_badges_for_context(self, badges):
        """
        Format user badges data for AI context.
        
        Args:
            badges (list): List of badge dictionaries
            
        Returns:
            str: Formatted badge context string
        """
        if not badges:
            return "No badges earned yet."
        
        formatted = [f"- {badge['Name']}: {badge['Description']}" for badge in badges]
        return "\n".join(formatted)
    
    def _format_all_badges_for_context(self, badges):
        """
        Format all available badges for AI context.
        
        Args:
            badges (list): List of badge dictionaries
            
        Returns:
            str: Formatted badge context string
        """
        if not badges:
            return "No badges available."
        
        formatted = [f"- {badge['Name']}: {badge['Description']}" for badge in badges[:20]]
        return "\n".join(formatted)
    
    # ============================================================================
    # Prompt Building
    # ============================================================================
    
    def _build_events_prompt(self, user_message, events_context, event_count):
        """
        Build AI prompt for Events category.
        
        Args:
            user_message (str): User's message
            events_context (str): Formatted events context
            event_count (int): Number of events found
            
        Returns:
            str: Complete prompt for AI
        """
        return f"""You are a helpful assistant for OneSky, a volunteering platform.

User's question: {user_message}

Available events from database ({event_count} found):
{events_context}

IMPORTANT - Event Registration Process:
When users ask to "sign up", "register", or "join" an event, they mean registering for a volunteer event:
1. Go to the Events page via the header menu
2. Find the event you want
3. Click Register (or Volunteer)
4. The event will appear in your upcoming events on the home dashboard

DO NOT confuse this with account sign-up. If they ask about "signing up for an event" or "registering for an event", they mean registering for a volunteer event, NOT creating an account.

Instructions:
- Keep your response CONCISE and DIRECT - 2-3 short paragraphs maximum
- Only provide information directly relevant to the user's question
- If events are found, briefly mention 1-2 most relevant events with date, time, and location
- If no events match, give a brief, helpful suggestion (1 sentence)
- If they ask about "signing up", "registering", or "joining" an event: ALWAYS use the Event Registration Process above - direct them to Events page in header, find the event, click Register - it will appear in upcoming events on home dashboard
- Use emojis sparingly (🎯 📍 📅 ⏰) - only when helpful
- When showing an event, format each piece of information on a separate line in the response (example format: Event Name, Date: 2025-01-01 on one line, Time: 10:00 on next line, Location: 123 Main St on next line)
- Be friendly but brief - no unnecessary explanations or fluff
- Focus ONLY on answering the user's specific question
- Do NOT list all events or provide excessive detail"""
    
    # ============================================================================
    # AI Response Handling
    # ============================================================================
    
    def get_ai_response(self, prompt):
        """
        Call OpenAI API to get response.
        
        Args:
            prompt (str): Complete prompt for AI
            
        Returns:
            str: AI-generated response
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5-nano",
                messages=[{"role": "user", "content": prompt}]
            )
            
            if response and response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                if message and message.content:
                    return message.content.strip()
            
            return "Sorry, I received an unexpected response from the AI. Please try again."
        except Exception as e:
            print(f"OpenAI API error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return f"Sorry, I'm having trouble processing your request right now. Error: {str(e)[:100]}"
