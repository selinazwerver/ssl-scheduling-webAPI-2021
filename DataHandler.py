import sqlite3
import csv
from datetime import datetime, timedelta
import math
import os
from os import path

class DataHandler():
    def __init__(self):
        return

    def date_to_hour(self, date):
        # Assumes that we start on Monday!
        timestamp = datetime.strptime(date, '%Y-%m-%d %H:%M')
        hour = (timestamp.timetuple().tm_wday * 24 + 24) - (24 - timestamp.timetuple().tm_hour)
        return math.floor(int(hour)/24), hour

    def hour_to_date(self, hour):
        # Assumes that we start on Monday!
        starttime = datetime.strptime('2021-06-21 00:00', '%Y-%m-%d %H:%M')
        date = starttime + timedelta(hours=hour)
        return str(date)[0:10], str(date)[11:-3] # date, time

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

    def get_db_connection(self, name):
        database = name + ".db"
        conn_schedule = sqlite3.connect(database)
        conn_schedule.row_factory = sqlite3.Row
        return conn_schedule

    def schedule_csv_to_db(self, name, removedb=False): # use this only once for the initial database
        filename = name + '.csv'
        conn = self.get_db_connection('schedule')
        cursor = conn.cursor()
        if (removedb): cursor.execute('DELETE FROM schedule')  # delete contents to avoid doubles
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for data in reader:
                data[3], data[4] = self.hour_to_date(int(data[4]))
                data[2] = self.field_number_to_letter(int(data[2]))
                cursor.execute('INSERT INTO schedule(day, teamA, teamB, starttime, field) VALUES (?,?,?,?,?)',
                            (data[3], data[0], data[1], data[4], data[2]))
            conn.commit()
            conn.close()

    def convert_db_functional_to_readable(self, name):
        # convert the hours in the database to a date/time format
        conn = self.get_db_connection(name)
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
        conn = self.get_db_connection(name)
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

    def export_db_to_csv(self, name):
        filename = name + ".csv"
        conn = self.get_db_connection(name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + name)
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(cursor)

    def export_friendly_to_csv(self, request):
        filename = 'friendly_request.csv'
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            day, hour = self.date_to_hour(request['day'] + ' ' + request['starttime'])
            writer.writerow([day, hour])

    def export_csv_to_db(self, name):
        filename = name + ".csv"
        conn = self.get_db_connection(name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ' + name) # delete contents to avoid doubles
        with open(filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            data = next(reader)
            query = 'insert into %s values ({0})' %(name)
            query = query.format(','.join('?' * len(data)))
            cursor.execute(query, data)
            for data in reader:
                cursor.execute(query, data)
            conn.commit()

    # Update the schedule database based on the 'new matches' csv
    # Write match to calendar
    # Write match to database
    def update_tournament_db(self):
        if path.exists('new_match.csv'):
            self.schedule_csv_to_db('new_match') # add data to database
            with open('new_match.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                for data in reader:
                    data[3], data[4] = self.hour_to_date(int(data[4]))
                    data[2] = self.field_number_to_letter(data[2])
                    # self.calHandler.write_event_to_calendar(teamA=data[0], teamB=data[1], field=data[2],
                    #                                         date=data[3], time=data[4], type='match')
            # remove new_match
            os.remove('new_match.csv')


        else:
            return