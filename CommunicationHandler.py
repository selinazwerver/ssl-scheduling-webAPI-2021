import csv
import math
from datetime import datetime, timedelta
from DataHandler import DataHandler
from CalendarHandler import CalendarHandler
# import thread

class CommunicationHandler():
    def __init__(self):  
        # self.sending_friendly_request = False
        self.dataHandler = DataHandler()
        self.calHandler = CalendarHandler()
        
        # Make csv files for sending/receiving friendly requests
        with open('friendly_request.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['code', 'hour'])

        # Start thread for sending the requests
        # thread.start_new_thread(self.find_oldest_friendly_request(), ("Thread-1", 2,))

    def convert_db_functional_to_readable(self, name):
        # convert the hours in the database to a date/time format
        conn = self.dataHandler.get_db_connection(name)
        cursor = conn.cursor()
        cursor2 = conn.cursor()
        for row in cursor.execute('SELECT * FROM ' + name):
            # print(row['day'], row['teamA'], row['teamB'], row['starttime'])
            if ((type(row['day']) == int) or (len(row['day']) < 3)): # do not update if it's already ok
                hour = row['starttime']
                date, time = self.dataHandler.hour_to_date(int(hour))
                field = self.dataHandler.field_number_to_letter(row['field'])
                cursor2.execute('UPDATE %s SET day = ?, starttime = ?, field = ? WHERE day = ? AND teamA = ? AND teamB = ? AND starttime = ?' %(name), 
                (date, time, field, row['day'], row['teamA'], row['teamB'], row['starttime']))
        conn.commit()
        conn.close()

    def convert_db_readable_to_functional(self, name):
        conn = self.dataHandler.get_db_connection(name)
        cursor = conn.cursor()
        cursor2 = conn.cursor()
        for row in cursor.execute('SELECT * FROM ' + name):
            if (len(row['day']) > 2): # do not update if it's already ok
                date = row['day']
                time = row['starttime']
                field = self.dataHandler.field_letter_to_number(row['field'])
                day, hour = self.dataHandler.date_to_hour(date + ' ' + time)
                cursor2.execute('UPDATE %s SET day = ?, starttime = ?, field = ? WHERE day = ? AND teamA = ? AND teamB = ? AND starttime = ?' %(name), 
                (date, time, field, row['day'], row['teamA'], row['teamB'], row['starttime']))
        conn.commit()
        conn.close()

    def find_oldest_friendly_request(self):
        # establish connection
        conn = self.dataHandler.get_db_connection('friendlies')
        cursor = conn.cursor()
        # cursor.execute('SELECT * FROM friendlies')
        cursor.execute('SELECT * FROM friendlies WHERE timestamp = (SELECT MIN(timestamp) FROM friendlies)')
        rows = cursor.fetchone()
        conn.commit()
        conn.close()

        return rows

    # Send friendly request
    # - Turn new friendly request to csv
    #
    def send_friendly_request(self):
        row = self.find_oldest_friendly_request()
        self.dataHandler.export_friendly_to_csv(row)

        # temp!
        self.calHandler.write_event_to_calendar(row)

        # if (self.send_friendly_request == False):
        #     do_stuff = 1

    # Receive friendly result
    def receive_friendly_request(self):
        return
        # self.send_friendly_request = True
        # get result from check from csv
        # update database with the new status

    # Send match results
    def send_match_results(self):
        # export results to csv
        # call some function to send csv to scheduler
        return