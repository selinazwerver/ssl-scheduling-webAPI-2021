import csv
import math
from datetime import datetime, timedelta
from os import popen
from re import sub
import subprocess

from googleapiclient.discovery import ResourceMethodParameters
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
        conn = self.dataHandler.get_db_connection('friendlies')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friendlies WHERE timestamp = (SELECT MIN(timestamp) FROM friendlies)')
        request = cursor.fetchone()
        conn.commit()
        conn.close()

        if (len(request) == 0):
            return 0
        elif (request['timestamp'] > datetime.now()):
            return 0
        else:
            return request

    # Send friendly request
    # - Turn new friendly request to csv
    #
    def send_friendly_request(self):
        request = self.find_oldest_friendly_request()

        if request == 0:
            return
        else:
            self.dataHandler.export_friendly_to_csv(request)
            result, newtime = 0, 0 # replace by binary call when we have that
            # popen = subprocess.Popen('name -c firendly_request.csv'.split(), stdout=subprocess.PIPE)
            # popen.wait()
            # result, newtime = popen.stdout.read()
            if result == 'accepted': # request is accepted, update calendar and database
                self.calHandler.write_event_to_calendar(request=request, type='friendly')
                conn = self.dataHandler.get_db_connection('friendlies')
                cursor = conn.cursor()
                cursor.execute('UPDATE friendlies SET status = ? WHERE status = ? AND day = ? AND teamA = ? AND teamB = ? AND starttime = ?', 
                ('Accepted', 'Pending', request['day'], request['teamA'], request['teamB'], request['starttime']))
                conn.commit()
                conn.close()
                return
            elif result == 'denied': # request is denied, update only database
                conn = self.dataHandler.get_db_connection('friendlies')
                cursor = conn.cursor()
                cursor.execute('UPDATE friendlies SET status = ? WHERE status = ? AND day = ? AND teamA = ? AND teamB = ? AND starttime = ?', 
                ('Denied', 'Pending', request['day'], request['teamA'], request['teamB'], request['starttime']))
                conn.commit()
                conn.close()
                return
            elif result == 'try again': # update timestamp to new time
                newday, newtime = self.dataHandler.hour_to_date(newtime)
                conn = self.dataHandler.get_db_connection('friendlies')
                cursor = conn.cursor()
                cursor.execute('UPDATE friendlies SET timestamp = ? WHERE status = ? AND day = ? AND teamA = ? AND teamB = ? AND starttime = ?', 
                (newday + ' ' + newtime, 'Pending', request['day'], request['teamA'], request['teamB'], request['starttime']))
                conn.commit()
                conn.close()
                return

        # temp!
        # self.calHandler.write_event_to_calendar(request)

    # Send match results
    def send_match_results(self):
        # export results to csv
        # call some function to send csv to scheduler
        return

    def receive_tournament_update(self):
        return