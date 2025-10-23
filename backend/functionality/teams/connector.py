import json
from data_access import DataAccess  

""" Middle layer between routes and data access """


class Connector():
    
    """Passes users email and team id to dao"""
    def add_user_to_team(self, user_email, team_id):
        dao = DataAccess()
        dao.insert_user_in_team(user_email, team_id)

    """Pass user input code to dao for verification"""
    def verify_team_code(self, team_id, join_code):
        dao = DataAccess()
        actual_code = dao.get_team_code(team_id)
        return actual_code == join_code
    
    # """ Passes teams user has joined"""
    # def user_joined_teams(self, user_email):
    #     dao = DataAccess()
    #     data_tuple_of_tuple = dao.get_all_joined_teams(user_email)
    #     all_teams = [x[0] for x in data_tuple_of_tuple]
    #     return all_teams
