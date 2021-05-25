import sqlite3
import csv
from datetime import datetime, timedelta
import math

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

    def get_db_connection(self, name):
        database = name + ".db"
        conn_schedule = sqlite3.connect(database)
        conn_schedule.row_factory = sqlite3.Row
        return conn_schedule

    def export_db_to_csv(self, name):
        filename = name + ".csv"
        conn = self.get_db_connection(name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + name)
        with open(filename, "w", newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(cursor)

    def export_friendly_to_csv(self, request):
        filename =  'friendly_request.csv'
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            for row in request:
                day, hour = self.date_to_hour(row['day'] + ' ' + row['starttime'])
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
