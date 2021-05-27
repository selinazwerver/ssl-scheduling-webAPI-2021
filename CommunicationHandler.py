import csv
import math
from datetime import datetime, timedelta
from os import popen
from re import sub
import subprocess
from DataHandler import DataHandler
from CalendarHandler import CalendarHandler
import threading

class CommunicationHandler():
    def __init__(self):  
        self.dataHandler = DataHandler()
        self.calHandler = CalendarHandler()

        self.new_match_results = False # true if new match results are in
        
        # Make csv files for sending/receiving friendly requests
        with open('friendly_request.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['code', 'hour'])

    def update(self): # functions that need to be checked regularly
        print('update!')
        self.send_friendly_request()
        self.receive_tournament_update()

        if self.new_match_results:
            self.new_match_results = False
            # run some binary I guess



    def find_oldest_friendly_request(self):
        conn = self.dataHandler.get_db_connection('friendlies')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friendlies WHERE timestamp = (SELECT MIN(timestamp) FROM friendlies)')
        request = cursor.fetchone()
        conn.commit()
        conn.close()

        if (len(request) == 0):
            return 0
        elif (datetime.strptime(request['timestamp'], '%Y-%m-%d %H:%M:%S.%f') > datetime.now()):
            return 0
        else:
            return request

    def send_friendly_request(self):
        request = self.find_oldest_friendly_request()

        if request == 0:
            return
        else:
            self.dataHandler.export_friendly_to_csv(request)
            result, newtime, field = 0, 0, 0 # replace by binary call when we have that
            # popen = subprocess.Popen('name -c firendly_request.csv'.split(), stdout=subprocess.PIPE)
            # popen.wait()
            # result, newtime, field = popen.stdout.read()
            if result == 'accepted': # request is accepted, update calendar and database
                self.calHandler.write_event_to_calendar(teamA=request['teamA'], teamB=request['teamB'],
                                                        date=request['day'], time=request['starttime'],
                                                        field=field, type='friendly')
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

    def receive_tournament_update(self):
        self.dataHandler.update_tournament_db()
        return