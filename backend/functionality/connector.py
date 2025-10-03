from data_access import DataAccess

class Connector():

    def extract_event_details(self):
        da = DataAccess()
        result = da.get_event_details()
        return result

if __name__ == "__main__":
    con = Connector()
    print(con.extract_event_details())
        