"""
Chatbot Connector
Handles chatbot logic for categorizing and responding to user queries.
Supports Events, Teams, Badges, Impact, and General categories.
"""
import os
import re
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from data_access import DataAccess
from .embedding_helper import EmbeddingHelper

load_dotenv()

# Module-level cache for category embeddings (shared across all instances)
_category_embeddings_cache = {}
_category_embeddings_initialized = False


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
            "what can I volunteer for"
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
            "what are the upcoming events for my teams"
        ],
        "badges": [
            "what badges do I have",
            "show my achievements",
            "my earned badges",
            "badges I've earned",
            "what achievements can I get",
            "view my badges",
            "how does badges work",
            "what badges are available"
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
            "show my impact"
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
            "how does this platform work"
        ]
    }
    
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
        
        # Initialize category embeddings only once (shared across all instances)
        global _category_embeddings_cache, _category_embeddings_initialized
        if not _category_embeddings_initialized:
            _category_embeddings_cache = self._initialize_category_embeddings()
            _category_embeddings_initialized = True
        
        # Use the shared cache
        self.category_embeddings = _category_embeddings_cache
    
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
            tuple: (response_text, category, events_list, teams_list, badges_list) - AI response, detected category, and lists for events/teams/badges
                   For non-matching categories, the respective list will be None
        """
        category, message_embedding = self._classify_intent_with_ai(user_message)
        
        # Route to appropriate category handler
        # For events, pass the embedding to reuse it (saves one API call)
        if category == "events":
            response, events_list = self._handle_events_category(user_message, user_email, message_embedding)
            return response, category, events_list, None, None
        elif category == "teams":
            response, teams_list = self._handle_teams_category(user_message, user_email)
            return response, category, None, teams_list, None
        elif category == "badges":
            response, badges_list = self._handle_badges_category(user_message, user_email)
            return response, category, None, None, badges_list
        elif category == "impact":
            response = self._handle_impact_category(user_message, user_email)
        else:  # general
            response = self._handle_general_category(user_message)
        
        return response, category, None, None, None
    
    # ============================================================================
    # Intent Classification
    # ============================================================================
    
    def _initialize_category_embeddings(self):
        """
        Generate and cache embeddings for category example texts at startup.
        Creates representative embeddings for each category by averaging example embeddings.
        Only called once when first instance is created.
        
        Returns:
            dict: Dictionary mapping category names to their averaged embeddings
        """
        category_embeddings = {}
        try:
            for category, examples in self.CATEGORY_EXAMPLES.items():
                # Generate embeddings for all examples in this category
                example_embeddings = []
                for example_text in examples:
                    embedding = self.embedding_helper.generate_embedding(example_text)
                    if embedding:
                        example_embeddings.append(embedding)
                
                if example_embeddings:
                    # Average the embeddings to create a category representation
                    # This creates a single embedding that represents the category
                    avg_embedding = np.mean(example_embeddings, axis=0).tolist()
                    category_embeddings[category] = avg_embedding
                else:
                    print(f"Warning: Could not generate embeddings for category: {category}")
        except Exception as e:
            print(f"Error initializing category embeddings: {e}")
            # Return empty dict - will fall back to keyword classification
        
        return category_embeddings
    
    def _classify_intent_with_ai(self, message):
        """
        Use embeddings-based classification to categorize user intent.
        Compares user message embedding with cached category embeddings.
        
        Args:
            message (str): User message
            
        Returns:
            tuple: (category, message_embedding) - Category name and embedding (can be None)
                   The embedding is returned so it can be reused for events search
        """
        if not message or not message.strip():
            return ("general", None)
        
        # If category embeddings weren't initialized, fall back to keyword classification
        if not self.category_embeddings:
            print("Category embeddings not available, using fallback classification")
            return (self._classify_intent_fallback(message), None)
        
        try:
            # Generate embedding for user message
            message_embedding = self.embedding_helper.generate_embedding(message)
            
            if not message_embedding:
                # If embedding generation fails, use fallback
                return (self._classify_intent_fallback(message), None)
            
            # Compare with each category embedding and find the best match
            best_category = "general"
            best_similarity = -1.0
            
            for category, category_embedding in self.category_embeddings.items():
                similarity = self.embedding_helper.cosine_similarity(
                    message_embedding, 
                    category_embedding
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_category = category
            
            # If similarity is too low, might be unclear intent - use general
            # Threshold of 0.3 ensures reasonable confidence
            if best_similarity < 0.3:
                return ("general", message_embedding)
            
            return (best_category, message_embedding)
            
        except Exception as e:
            print(f"Error in embedding-based classification: {e}")
            return (self._classify_intent_fallback(message), None)
    
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
    
    def _handle_events_category(self, user_message, user_email=None, query_embedding=None):
        """
        Handle Events category - find and search volunteer events.
        
        Args:
            user_message (str): User's message
            user_email (str, optional): User's email
            query_embedding (list, optional): Pre-generated embedding to reuse (saves API call)
            
        Returns:
            tuple: (response_text, events_list) - AI response text and list of event dictionaries
        """
        location = self._extract_location(user_message)
        
        # Detect if user wants a single event
        wants_single_event = self._detect_single_event_request(user_message)
        
        # Reuse embedding if provided, otherwise generate new one
        if not query_embedding:
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
        system_prompt = self._build_system_prompt()
        
        # Determine event count for display
        limit = 1 if wants_single_event else 3
        event_count_display = min(len(events), limit)
        
        prompt = f"""{system_prompt}

User's question: {user_message}

Available events from database ({len(events)} found):
{formatted_events}

IMPORTANT - Event Registration Process:
When users ask to "sign up", "register", or "join" an event, they mean registering for a volunteer event:
1. Go to the Events page via the header menu
2. Find the event you want
3. Click Register (or Volunteer)
4. The event will appear in your upcoming events on the home dashboard

DO NOT confuse this with account sign-up. If they ask about "signing up for an event" or "registering for an event", they mean registering for a volunteer event, NOT creating an account.

CRITICAL - Response Formatting:
- Events will be displayed as interactive cards below your message, so DO NOT mention specific event details (title, date, time, location) in your text response
- Instead, provide a brief introductory message such as:
  * If showing events: "Here are some events matching what you asked for:" or "Here are events that match your criteria:" or similar
  * If showing one event: "Here's an event matching what you asked for:" or "Here's an event that might interest you:" or similar
  * If no events found: Briefly suggest checking the Events section or trying different search terms
- Keep your response CONCISE - just 1-2 sentences maximum
- Do NOT list event details, dates, times, or locations in your text - those will be shown in the event cards
- Be friendly and brief"""
        
        response_text = self.get_ai_response(prompt)
        
        # Return events list - limit based on user request
        # Default: 2-3 events, but if user asks for "one", "a", or "an" event, show only 1
        events_list = []
        if events:
            limit = 1 if wants_single_event else 3  # Show 1 if single requested, otherwise up to 3
            for event in events[:limit]:
                event_dict = dict(event) if not isinstance(event, dict) else event
                events_list.append(event_dict)
        
        return response_text, events_list
    
    def _detect_single_event_request(self, message):
        """
        Detect if user is asking for a single event (e.g., "a event", "an event", "one event").
        
        Args:
            message (str): User's message
            
        Returns:
            bool: True if user wants a single event, False otherwise
        """
        if not message:
            return False
        
        message_lower = message.lower()
        
        # Check for single event indicators
        single_event_patterns = [
            r'\b(a|an)\s+(event|volunteer|opportunity|activity)',
            r'\bone\s+(event|volunteer|opportunity|activity)',
            r'\b(a|an)\s+volunteering',
            r'\bone\s+volunteering',
            r'\bshow\s+me\s+(a|an|one)',
            r'\bfind\s+me\s+(a|an|one)',
            r'\bgive\s+me\s+(a|an|one)',
            r'\bsuggest\s+(a|an|one)',
            r'\brecommend\s+(a|an|one)',
        ]
        
        for pattern in single_event_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _handle_teams_category(self, user_message, user_email=None):
        """Handle Teams category - team-related queries."""
        # Fetch team data if user is logged in
        user_teams = []
        all_teams = []
        team_events = []
        
        if user_email:
            try:
                user_teams = self.dao.get_all_joined_teams(user_email)
                all_teams = self.dao.get_all_teams()
                team_events = self.dao.get_team_events(user_email)
            except Exception as e:
                print(f"Error fetching team data: {e}")
        
        # Detect if user wants all teams or a specific team
        wants_all_teams = self._detect_all_teams_request(user_message)
        wants_single_team = self._detect_single_team_request(user_message)
        
        # Check if user is asking for a specific team by name (even without "a team" phrase)
        matching_team_by_name = self._find_matching_team(user_message, all_teams)
        
        # Determine which teams to return
        teams_to_return = []
        if wants_all_teams:
            # User wants all available teams
            teams_to_return = all_teams[:10] if all_teams else []
        elif matching_team_by_name:
            # User mentioned a specific team name - return that team
            teams_to_return = [matching_team_by_name]
        elif wants_single_team:
            # User wants a single team but no specific name matched - return first team
            teams_to_return = all_teams[:1] if all_teams else []
        else:
            # Default: show user's teams if asking about "my teams", otherwise show all
            if self._is_asking_about_my_teams(user_message):
                teams_to_return = user_teams[:5] if user_teams else []
            else:
                # Show a few teams as suggestions
                teams_to_return = all_teams[:3] if all_teams else []
        
        formatted_user_teams = self._format_teams_for_context(user_teams)
        formatted_all_teams = self._format_teams_for_context(all_teams[:10]) if all_teams else "No teams available"
        formatted_team_events = self._format_events_for_context(team_events) if team_events else "No team events"
        
        system_prompt = self._build_system_prompt()
        
        prompt = f"""{system_prompt}

User's question: {user_message}

IMPORTANT - Team Instructions:

**Joining a Team:**
Go to Teams in the header menu, browse available teams, and join using a join code.

**Creating a Team:**
Go to Teams in the header menu, click on "Create Team" in the My Teams section, fill in the details (name, description, department, capacity), click Create, and share the join code with others so they can join.

**Registering as a Team for an Event:**
The team owner can go to Events in the header menu, find an event, click on "Register as a Team" to register the team to that event.

User's teams ({len(user_teams)}):
{formatted_user_teams}

Available teams (showing first 10):
{formatted_all_teams}

Events your teams are registered for:
{formatted_team_events}

CRITICAL - Response Formatting:
- Teams will be displayed as interactive cards below your message, so DO NOT mention specific team details (name, description, department) in your text response
- Instead, provide a brief introductory message such as:
  * If showing teams: "Here are some teams matching what you asked for:" or "Here are teams that match your criteria:" or similar
  * If showing one team: "Here's a team matching what you asked for:" or "Here's a team that might interest you:" or similar
  * If no teams match: Briefly suggest checking the Teams section
- Keep your response CONCISE - just 1-2 sentences maximum
- Do NOT list team details in your text - those will be shown in the team cards
- Be friendly and brief"""
        
        response_text = self.get_ai_response(prompt)
        
        # Return teams list (convert to dict format for frontend)
        teams_list = []
        # Get user_id for owner checking
        user_id = None
        if user_email:
            try:
                user_id = self.dao.get_user_id_by_email(user_email)
            except Exception as e:
                print(f"Error getting user ID: {e}")
        
        for team in teams_to_return:
            team_dict = dict(team) if not isinstance(team, dict) else team
            # Ensure proper field names for TeamCard component
            if 'ID' in team_dict:
                team_dict['id'] = team_dict['ID']
            if 'Name' in team_dict:
                team_dict['name'] = team_dict['Name']
            if 'JoinCode' in team_dict:
                team_dict['join_code'] = team_dict['JoinCode']
            # Check if user is owner (if not already set)
            if 'IsOwner' not in team_dict or team_dict['IsOwner'] is None:
                if user_id and 'OwnerUserID' in team_dict:
                    team_dict['is_owner'] = (team_dict['OwnerUserID'] == user_id)
                elif 'IsOwner' in team_dict:
                    team_dict['is_owner'] = team_dict['IsOwner']
                else:
                    team_dict['is_owner'] = False
            else:
                team_dict['is_owner'] = team_dict['IsOwner']
            teams_list.append(team_dict)
        
        return response_text, teams_list
    
    def _detect_all_teams_request(self, message):
        """Detect if user is asking for all teams."""
        if not message:
            return False
        
        message_lower = message.lower()
        all_teams_patterns = [
            r'\ball\s+teams',
            r'\bevery\s+team',
            r'\bshow\s+(all|every)\s+teams',
            r'\blist\s+(all|every)\s+teams',
            r'\bbrowse\s+(all|every)\s+teams',
            r'\bwhat\s+teams\s+(are\s+there|exist|available)',
        ]
        
        for pattern in all_teams_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _detect_single_team_request(self, message):
        """Detect if user is asking for a single team."""
        if not message:
            return False
        
        message_lower = message.lower()
        single_team_patterns = [
            r'\b(a|an)\s+team',
            r'\bone\s+team',
            r'\bshow\s+me\s+(a|an|one)\s+team',
            r'\bfind\s+me\s+(a|an|one)\s+team',
            r'\bgive\s+me\s+(a|an|one)\s+team',
        ]
        
        for pattern in single_team_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _is_asking_about_my_teams(self, message):
        """Detect if user is asking about their own teams."""
        if not message:
            return False
        
        message_lower = message.lower()
        my_teams_patterns = [
            r'\bmy\s+teams',
            r'\bteams\s+I\s+(am\s+in|joined|belong\s+to)',
            r'\bteams\s+I\'m\s+in',
            r'\bwhat\s+teams\s+(am\s+I|do\s+I\s+have|am\s+I\s+part\s+of)',
        ]
        
        for pattern in my_teams_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _find_matching_team(self, message, all_teams):
        """
        Find a team matching the user's query by name.
        Uses flexible matching: exact match, word-boundary match, or partial match.
        
        Args:
            message (str): User's message
            all_teams (list): List of all teams
            
        Returns:
            dict or None: Matching team dictionary, or None if no match found
        """
        if not all_teams:
            return None
        
        message_lower = message.lower().strip()
        
        # Remove common query words to extract potential team name
        query_words = ['team', 'teams', 'show', 'find', 'get', 'tell', 'me', 'about', 
                      'the', 'a', 'an', 'is', 'are', 'what', 'which', 'who', 'how']
        words = [w for w in message_lower.split() if w not in query_words and len(w) > 2]
        potential_team_name = ' '.join(words).strip()
        
        best_match = None
        best_score = 0
        
        for team in all_teams:
            team_name = (team.get('Name') or team.get('name') or '').strip()
            if not team_name:
                continue
                
            team_name_lower = team_name.lower()
            score = 0
            
            # Exact match (highest priority)
            if team_name_lower == message_lower or team_name_lower == potential_team_name:
                score = 100
            # Word boundary match (e.g., "Marketing Team" matches "marketing")
            elif re.search(r'\b' + re.escape(team_name_lower) + r'\b', message_lower):
                score = 80
            # Team name contains query words (e.g., "marketing" in "Marketing Team")
            elif all(word in team_name_lower for word in words if len(word) > 2):
                score = 60
            # Partial match - team name contains in message or vice versa
            elif team_name_lower in message_lower:
                score = 50
            elif any(word in team_name_lower for word in words if len(word) > 2):
                score = 40
            
            if score > best_score:
                best_score = score
                best_match = team
        
        # Only return match if score is high enough (at least 40)
        return best_match if best_score >= 40 else None
    
    def _handle_badges_category(self, user_message, user_email=None):
        """Handle Badges category - user badges and achievements."""
        if not user_email:
            return "Please log in to view your badges and achievements.", None
        
        user_id = self.dao.get_user_id_by_email(user_email)
        if not user_id:
            return "Unable to retrieve your account information. Please try again.", None
        
        user_badges = self.dao.get_badges(user_id)
        all_badges = self.dao.get_all_badges()
        
        # Detect if user is asking about their badges or all available badges
        is_asking_about_my_badges = self._is_asking_about_my_badges(user_message)
        is_asking_about_all_badges = self._is_asking_about_all_badges(user_message)
        
        # Determine which badges to return
        badges_to_return = []
        if is_asking_about_my_badges:
            # User wants their earned badges
            badges_to_return = user_badges[:5] if user_badges else []  # Limit to 5 for display
        elif is_asking_about_all_badges:
            # User wants to see next badges they could earn (not already earned)
            # Create set of user's badge IDs (handle both dict keys and ensure int comparison)
            user_badge_ids = set()
            for badge in user_badges:
                badge_id = badge.get('ID') or badge.get('id')
                if badge_id:
                    user_badge_ids.add(int(badge_id))  # Convert to int for comparison
            
            # Filter out badges user already has
            available_badges = []
            for badge in all_badges:
                badge_id = badge.get('ID') or badge.get('id')
                if badge_id:
                    badge_id_int = int(badge_id)
                    if badge_id_int not in user_badge_ids:
                        available_badges.append(badge)
            
            badges_to_return = available_badges[:2] if available_badges else []  # Next 2 badges
        else:
            # Default: show user's badges if they have any, otherwise show next 2 available
            if user_badges:
                badges_to_return = user_badges[:3] if len(user_badges) > 3 else user_badges
            else:
                # Show next 2 badges they could earn
                badges_to_return = all_badges[:2] if all_badges else []
        
        formatted_user_badges = self._format_badges_for_context(user_badges)
        formatted_all_badges = self._format_all_badges_for_context(all_badges)
        
        system_prompt = self._build_system_prompt()
        
        prompt = f"""{system_prompt}

User's question: {user_message}

User's earned badges ({len(user_badges)} total):
{formatted_user_badges}

All available badges:
{formatted_all_badges}

CRITICAL - Response Formatting:
- Badges will be displayed as interactive cards below your message, so DO NOT mention specific badge details (name, description) in your text response
- Instead, provide a brief introductory message such as:
  * If showing user's badges: "Here are your earned badges:" or "Here are the badges you've earned:" or similar
  * If showing available badges: "Here are some badges you could earn:" or "Here are badges you can work towards:" or similar
  * If no badges: Briefly suggest volunteering to earn badges
- Keep your response CONCISE - just 1-2 sentences maximum
- Do NOT list badge details in your text - those will be shown in the badge cards
- Be friendly and brief"""
        
        response_text = self.get_ai_response(prompt)
        
        # Return badges list (convert to dict format for frontend)
        badges_list = []
        for badge in badges_to_return:
            badge_dict = dict(badge) if not isinstance(badge, dict) else badge
            # Ensure proper field names (ID should already be correct, but ensure consistency)
            if 'ID' in badge_dict and 'id' not in badge_dict:
                badge_dict['id'] = badge_dict['ID']
            badges_list.append(badge_dict)
        
        return response_text, badges_list
    
    def _is_asking_about_my_badges(self, message):
        """Detect if user is asking about their own badges."""
        if not message:
            return False
        
        message_lower = message.lower()
        my_badges_patterns = [
            r'\bmy\s+badges',
            r'\bbadges\s+I\s+(have|earned|got|own)',
            r'\bbadges\s+I\'ve\s+(earned|got)',
            r'\bwhat\s+badges\s+(do\s+I\s+have|have\s+I\s+earned|am\s+I\s+part\s+of)',
            r'\bshow\s+my\s+badges',
        ]
        
        for pattern in my_badges_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _is_asking_about_all_badges(self, message):
        """Detect if user is asking about all available badges."""
        if not message:
            return False
        
        message_lower = message.lower().strip()
        
        # Use simple keyword-based detection (more reliable than regex)
        # Keywords that indicate asking about available badges
        available_keywords = [
            'can', 'could', 'earn', 'get', 'obtain', 'unlock', 
            'available', 'other', 'more', 'additional', 'what badges',
            'which badges', 'don\'t have', 'haven\'t', 'missing'
        ]
        
        # Keywords that explicitly indicate asking about owned badges
        my_badges_keywords = ['my badges', 'have', 'earned', 'got', 'own', 'show my']
        
        # Check if it explicitly asks about owned badges first
        if any(keyword in message_lower for keyword in my_badges_keywords):
            # But exclude if it also has "can earn" type phrases
            if not any(word in message_lower for word in ['can', 'could', 'earn', 'get']):
                return False
        
        # Check if query contains available keywords
        if any(keyword in message_lower for keyword in available_keywords):
            print(f"DEBUG: Detected as 'all badges' query: '{message_lower}'")
            return True
        
        print(f"DEBUG: Not detected as 'all badges' query: '{message_lower}'")
        return False
    
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
        
        system_prompt = self._build_system_prompt()
        
        prompt = f"""{system_prompt}

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

NOTE: Only show stats, no events, teams or anything else.
"""
        
        return self.get_ai_response(prompt)
    
    def _handle_general_category(self, user_message):
        """Handle General category - platform help, navigation, greetings."""
        system_prompt = self._build_system_prompt()
        
        prompt = f"""{system_prompt}

User's question: {user_message}"""
        
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
    
    def _format_teams_for_context(self, teams):
        """
        Format teams data for AI context.
        
        Args:
            teams (list): List of team dictionaries
            
        Returns:
            str: Formatted team context string
        """
        if not teams:
            return "No teams found."
        
        formatted = []
        for team in teams[:10]:
            team_str = f"Team ID {team['ID']}: {team.get('Name', 'Unnamed Team')}"
            if team.get('Description'):
                team_str += f" - {team['Description'][:100]}"
            if team.get('Department'):
                team_str += f" - Department: {team['Department']}"
            formatted.append(team_str)
        
        return "\n".join(formatted)
    
    # ============================================================================
    # Prompt Building
    # ============================================================================
    
    def _build_system_prompt(self):
        """
        Build the shared system prompt for all handlers.
        
        Returns:
            str: Base system prompt shared across all categories
        """
        return """You are OneSky Assistant, the helpful chatbot for OneSky — Sky's internal volunteering platform where employees can find volunteering opportunities, track impact, earn badges, and collaborate in teams.
All navigation and features can be accessed from the header menu at the top of the page.

When responding:
- Be concise, direct, and friendly — no filler or unrelated info.
- Only provide information relevant to the user's query.
- Use emoji sparingly when helpful (never excessive).
- Always stay within OneSky context — do not answer general or external questions.

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
"I'm sorry, I can only help with volunteering events and features on the OneSky platform."""
    
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
