import csv
import math
from datetime import datetime, timedelta
from DataHandler import DataHandler

class CommunicationHandler():
    def __init__(self):  
        self.sending_friendly_request = False
        self.dataHandler = DataHandler()
        
        # Make csv files for sending/receiving friendly requests
        with open('friendly_request.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['code', 'hour'])

    def date_to_hour(self, date):
        # Assumes that we start on Monday!
        timestamp = datetime.strptime(date, '%Y-%m-%d %H:%M')
        hour = (timestamp.timetuple().tm_wday*24 + 24) - (24 - timestamp.timetuple().tm_hour)
        return math.floor(int(hour)/24), hour

    def hour_to_date(self, hour):
        # Assumes that we start on Monday!
        starttime =  datetime.strptime('2021-06-21 00:00', '%Y-%m-%d %H:%M')
        date = starttime + timedelta(hours=hour)
        return str(date)[0:10], str(date)[11:-3]

    def convert_db_to_normal_time(self, name):
        # convert the hours in the database to a date/time format
        conn = self.dataHandler.get_db_connection(name)
        cursor = conn.cursor()
        cursor2 = conn.cursor()
        for row in cursor.execute('SELECT * FROM ' + name):
            if (type(row['day']) == int): # do not update if it's already ok
                hour = row['starttime']
                date, time = self.hour_to_date(int(hour))
                print(date, time)            
                cursor2.execute('UPDATE %s SET day = ?, starttime = ?' %(name), (date, time))
        conn.commit()
        conn.close()

    def convert_db_to_hours_time(self,name):
        conn = self.dataHandler.get_db_connection(name)
        cursor = conn.cursor()
        cursor2 = conn.cursor()
        for row in cursor.execute('SELECT * FROM ' + name):
            if (len(row['day']) > 2): # do not update if it's already ok
                date = row['day']
                time = row['starttime']
                day, hour = self.date_to_hour(date + ' ' + time)
                print(date, time)            
                cursor2.execute('UPDATE %s SET day = ?, starttime = ?' %(name), (day, hour))
        conn.commit()
        conn.close()

    def find_oldest_request(self):
        # establish connection
        # conn = ....
        # cursor = conn.cursor()
        # cursor.execute('SELECT min(timestamp) FROM friendlies WHERE status = Pending')
        # rows = cursor.fetchall()
        # conn.commit()
        # conn.close()

        # if len(rows == 0):
            # there are no requests


        # rows to excel sheet
        # send request
        return

    # Send friendly request
    # - Turn new friendly request to csv
    #
    def send_friendly_request(self):
        if (self.send_friendly_request == False):
            do_stuff = 1 

    # Receive friendly result
    def receive_friendly_request(self):
        self.send_friendly_request = True
        # get result from check from csv
        # update database with the new status

    # Send match results
    def send_match_results(self):
        # export results to csv
        # call some function to send csv to scheduler
        return