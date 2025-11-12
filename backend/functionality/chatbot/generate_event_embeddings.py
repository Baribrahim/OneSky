"""
Script to generate and store embeddings for all events in the database.

Run this script once to populate embeddings for all existing events.
When new events are added, you can run this again or integrate embedding
generation into the event creation process.

Usage:
    python3 -m chatbot.generate_event_embeddings
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_access import DataAccess
from chatbot.embedding_helper import EmbeddingHelper

# Load .env but don't override existing env vars (for Docker compatibility)
load_dotenv(override=False)

# For local development, use localhost instead of external IP
if os.getenv("MYSQL_HOST") == "35.210.202.5" and not os.getenv("DOCKER_ENV"):
    os.environ["MYSQL_HOST"] = "localhost"
    if os.getenv("MYSQL_PORT") == "3306":
        os.environ["MYSQL_PORT"] = "3301"


def generate_all_event_embeddings():
    """Generate and store embeddings for all events"""
    dao = DataAccess()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it")
        return
    
    embedding_helper = EmbeddingHelper(api_key)
    
    # Get all events that need embeddings
    events = dao.get_all_events_for_embedding()
    
    if not events:
        print("No events found in database")
        return
    
    print(f"Found {len(events)} events to process")
    
    success_count = 0
    error_count = 0
    
    for event in events:
        event_id = event['ID']
        event_text = event['text']
        
        if not event_text:
            print(f"Skipping event {event_id}: No text content")
            continue
        
        print(f"Processing event {event_id}: {event.get('text', '')[:50]}...")
        
        # Generate embedding
        embedding = embedding_helper.generate_embedding(event_text)
        
        if embedding:
            # Store embedding
            dao.store_event_embedding(event_id, embedding)
            success_count += 1
            print(f"✓ Stored embedding for event {event_id}")
        else:
            error_count += 1
            print(f"✗ Failed to generate embedding for event {event_id}")
    
    print(f"\n=== Summary ===")
    print(f"Successfully processed: {success_count} events")
    print(f"Errors: {error_count} events")
    print(f"Total: {len(events)} events")


if __name__ == "__main__":
    print("Starting embedding generation for all events...")
    print("=" * 50)
    
    try:
        generate_all_event_embeddings()
        print("\n✓ Embedding generation complete!")
    except Exception as e:
        print(f"\n✗ Error during embedding generation: {e}")
        import traceback
        traceback.print_exc()
