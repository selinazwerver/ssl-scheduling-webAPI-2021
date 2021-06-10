import csv
import math
from datetime import datetime, timedelta
from os import popen
from re import sub
import subprocess
import threading

from googleapiclient.http import RequestMockBuilder
from DataHandler import DataHandler
from CalendarHandler import CalendarHandler
import time

class CommunicationHandler():
    def __init__(self):  
        self.dataHandler = DataHandler()
        self.calHandler = CalendarHandler()
        self.lock = threading.Lock()

        self.new_match_results = False # true if new match results are in

    def update(self): # functions that need to be checked regularly
        while True:
            # self.send_friendly_request()
            self.receive_tournament_update()

            if self.new_match_results:
                print('[CommHandler][update] Sending new match results')
                self.new_match_results = False
                self.lock.acquire()
                self.dataHandler.export_schedule_to_csv()
                # run some binary I guess
                self.lock.release()
                print('[CommHandler][update] Done sending new match results')

            time.sleep(5) # change to the time we want

    def find_oldest_friendly_request(self):
        conn = self.dataHandler.get_db_connection('friendlies')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friendlies WHERE status = ? GROUP BY timestamp HAVING MIN(timestamp)', ('Pending',))
        request = cursor.fetchone()
        conn.commit()
        conn.close()

        if request is None: # no requests
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
            # self.dataHandler.export_friendly_to_csv(request)
            # export friendly date to hour
            day, hour = self.dataHandler.date_to_hour(request['day'] + ' ' + request['starttime'])
            print('[CommHandler][send_friendly_request] Sending new friendly request')
            self.lock.acquire()
            result, newtime, field = 'accepted', 0, 0 # replace by binary call when we have that
            # popen = subprocess.Popen('name -c firendly_request.csv'.split(), stdout=subprocess.PIPE)
            # popen.wait()
            # result, newtime, field = popen.stdout.read()
            self.lock.release()
            print('[CommHandler][send_friendly_request] Friendly request is:', result)

            if result == 'accepted': # request is accepted, update calendar and database
                self.dataHandler.update_team_availability(type='list', data=[request['teamA'], request['teamB'], hour]) # update availability
                field = self.dataHandler.field_number_to_letter(field)
                # self.calHandler.write_event_to_calendar(teamA=request['teamA'], teamB=request['teamB'],
                                                        # date=request['day'], time=request['starttime'],
                                                        # field=field, type='friendly')
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

    def receive_tournament_update(self):
        self.dataHandler.update_tournament_db()
        return