import json
import bcrypt
     

# import sys
# import os

# # Add the parent directory to sys.path (optional, for direct script execution)
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_access import DataAccess  
""" Middle layer between routes and data access """


class EventConnector():
   
    def __init__(self, dao: DataAccess | None = None):
        self.dao = dao or DataAccess()

    """ Extracts events fields and values and formats as dictionary"""

    def extract_event_details(self):
        values, keys = self.dao.get_event_details()
        results = [dict(zip(keys, value)) for value in values]
        return results
    
    """Passes users email and event id to dao"""
    def register_user_for_event(self, user_email, event_id):
        self.dao.store_user_event_id(user_email, event_id)

    """ Passes events user is signed up for"""
    def user_signed_up_for_events(self, user_email):
        data_tuple_of_tuple = self.dao.get_user_events(user_email)
        flat_data = [x[0] for x in data_tuple_of_tuple]
        return flat_data

    """ Passes users email and event id to unregister from event"""
    def unregister_user_from_event(self, user_email, event_id):
        self.dao.delete_user_from_event(user_email, event_id)

    """Extracts team details where user is owner and team not signed up to event"""
    def extract_team_unregistered_details(self, user_email, event_id):
        return self.dao.read_user_unregistered_teams(event_id, user_email)

       
    """ Passes team id and event id to dao"""
    def register_team_for_event(self, team_id, event_id):
        self.dao.insert_team_to_event_registration(team_id, event_id)
    
    def get_user_id_by_email(self, email):
        return self.dao.get_user_id_by_email(email)
