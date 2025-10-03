import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='oneskyv1'
    )

def get_db_connection():
    mydb = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='oneskyv1'
    )
    return mydb

def get_location():
    conn = get_db_connection()
    cursor = conn.cursor()


    query = "SELECT LocationCity FROM event"
    cursor.execute(query)

    result_set = cursor.fetchall()
    location_list = [row[0] for row in result_set]
    conn.close()

    return location_list
