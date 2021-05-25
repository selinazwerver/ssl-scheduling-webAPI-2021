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

    def field_number_to_letter(self, number):
        if (number == 0): return 'A'
        if (number == 1): return 'B'
        if (number == 2): return 'C'
        if (number == 3): return 'D'

    def field_letter_to_number(self, letter):
        if (letter == 'A'): return 1
        if (letter == 'B'): return 2
        if (letter == 'C'): return 3
        if (letter == 'D'): return 4

    def convert_db_functional_to_readable(self, name):
        # convert the hours in the database to a date/time format
        conn = self.dataHandler.get_db_connection(name)
        cursor = conn.cursor()
        cursor2 = conn.cursor()
        for row in cursor.execute('SELECT * FROM ' + name):
            # print(row['day'], row['teamA'], row['teamB'], row['starttime'])
            if ((type(row['day']) == int) or (len(row['day']) < 3)): # do not update if it's already ok
                hour = row['starttime']
                date, time = self.hour_to_date(int(hour))
                field = self.field_number_to_letter(row['field'])
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
                field = self.field_letter_to_number(row['field'])
                day, hour = self.date_to_hour(date + ' ' + time)       
                cursor2.execute('UPDATE %s SET day = ?, starttime = ?, field = ? WHERE day = ? AND teamA = ? AND teamB = ? AND starttime = ?' %(name), 
                (date, time, field, row['day'], row['teamA'], row['teamB'], row['starttime']))
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