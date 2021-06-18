import threading
import time
import csv
import os
from datetime import datetime
from subprocess import Popen, PIPE

from CalendarHandler import CalendarHandler
from DataHandler import DataHandler


class CommunicationHandler():
    def __init__(self):
        self.dataHandler = DataHandler()
        self.calHandler = CalendarHandler()
        self.lock = threading.Lock()
        self.new_match_results = False  # true if new match results are in

    def update(self):  # functions that need to be checked regularly
        while True:
            print('[CommHandler][update]')
            self.send_friendly_request()
            self.receive_tournament_update()

            if self.new_match_results:
                print('[CommHandler][update] Sending new match results')
                self.new_match_results = False
                self.lock.acquire()
                self.dataHandler.export_schedule_to_csv()
                # Send new results to scheduler
                process = Popen(['data/ssl-scheduling/data/script.sh'], stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                print(stdout)
                print(stderr)
                process.wait()
                self.lock.release()
                print('[CommHandler][update] Done sending new match results')

            time.sleep(5)  # change to the time we want

    def find_oldest_friendly_request(self):
        conn = self.dataHandler.get_db_connection('friendlies')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM friendlies WHERE status = ? GROUP BY timestamp HAVING MIN(timestamp)',
                       ('Pending',))
        request = cursor.fetchone()
        conn.commit()
        conn.close()

        if request is None:  # no requests
            return 0
        elif (datetime.strptime(request['timestamp'], '%Y-%m-%d %H:%M:%S.%f') > datetime.now()):
            # request time is not passed (used for 'try again in x hours')
            return 0
        else:
            return request

    def send_friendly_request(self):
        request = self.find_oldest_friendly_request()

        if request == 0:
            return
        else:
            # export friendly date to hour
            day, hour = self.dataHandler.date_to_hour(request['day'] + ' ' + request['starttime'])
            print('[CommHandler][send_friendly_request] Sending new friendly request, hour =', hour)
            self.lock.acquire()
            # result, newtime, field = 'try again', 48, 0  # replace by part below when we have that
            process = Popen(['data/ssl-scheduling/data/script.sh', str(hour)], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            print(stdout)
            print(stderr)
            process.wait()
            self.lock.release()
            reader = csv.reader(open('data/friendly.csv', 'r'), delimiter=',')

            for data in reader:
                result = data[0]
                newtime = data[1]
                field = data[2]

            print('[CommHandler][send_friendly_request] Result request:', result)
            os.remove('data/friendly.csv')

            conn = self.dataHandler.get_db_connection('friendlies')
            cursor = conn.cursor()

            if result == 'accepted':  # request is accepted, update availability, calendar and database
                # update availability
                self.dataHandler.update_team_availability(type='list', data=[request['teamA'], request['teamB'],
                                                                             hour])  # update availability
                
                # write friendly to calendar
                field = self.dataHandler.field_number_to_letter(int(field))
                self.calHandler.write_event_to_calendar(teamA=request['teamA'], teamB=request['teamB'],
                date=request['day'], time=request['starttime'], field=field, type='friendly')

                # update database
                cursor.execute(
                    'UPDATE friendlies SET status = ?, field = ? WHERE status = ? AND day = ? AND teamA = ? AND teamB = ? AND starttime = ?',
                    ('Accepted', field, 'Pending', request['day'], request['teamA'], request['teamB'], request['starttime']))

            elif result == 'denied':  # request is denied, update only database
                cursor.execute(
                    'UPDATE friendlies SET status = ? WHERE status = ? AND day = ? AND teamA = ? AND teamB = ? AND starttime = ?',
                    ('Denied', 'Pending', request['day'], request['teamA'], request['teamB'], request['starttime']))

            elif result == 'try again':  # update timestamp in the database to new time
                # newtime is in absolute hours, convert to datetime structure
                print('[CommHandler][send_friendly_request] Try again at hour:', newtime)
                newday, newtime = self.dataHandler.hour_to_date(newtime)
                print('[CommHandler][send_friendly_request] Try again at date:', newday, newtime)

                cursor.execute(
                    'UPDATE friendlies SET timestamp = ? WHERE status = ? AND day = ? AND teamA = ? AND teamB = ? AND starttime = ?',
                    (newday + ' ' + newtime + ':0.0', 'Pending', request['day'], request['teamA'], request['teamB'],
                     request['starttime']))

            conn.commit()
            conn.close()
            return

    def receive_tournament_update(self):
        self.dataHandler.update_tournament_db()
        return
