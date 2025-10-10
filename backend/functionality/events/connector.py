import json
import bcrypt
     

# import sys
# import os

# # Add the parent directory to sys.path (optional, for direct script execution)
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_access import DataAccess  
""" Middle layer between routes and data access """


class Connector():

    """ Extracts events fields and values and formats as dictionary"""

    def extract_event_details(self):
        dao = DataAccess()
        values, keys = dao.get_event_details()
        results = [dict(zip(keys, value)) for value in values]
        return results
    
    """Passes users email and event id to dao"""

    def register_user_for_event(self, user_email, event_id):
        dao = DataAccess()
        dao.store_user_event_id(user_email, event_id)


ca = Connector()
ca.extract_event_details()
