import sqlite3
import csv
from datetime import datetime, timedelta
import math
import os
from os import path
from CalendarHandler import CalendarHandler

class DataHandler():
    def __init__(self):
        self.calHandler = CalendarHandler()

        self.team_names_to_row = {
            'ER-Force': 0,
            'RoboCIn': 1,
            'RoboTeam Twente': 2,
            'KIKS': 3,
            'TIGERs Mannheim': 4,
            'KgpKubs': 5,
            'RoboIME': 6,
            'RoboFEI': 7,
            'ITAndroids': 8,
            'UBC Thunderbots': 9,
            'RoboDragons': 10,
            'MRL': 11,
            'RoboJackets': 12,
            'Tritons RCSC': 13,
            'Omid': 14,
            'URoboRus': 15,
            'SRC': 16
        }

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
        if (letter == 'A'): return 0
        if (letter == 'B'): return 1
        if (letter == 'C'): return 2
        if (letter == 'D'): return 3

    def get_db_connection(self, name):
        database = name + ".db"
        conn_schedule = sqlite3.connect('data/' + database)
        conn_schedule.row_factory = sqlite3.Row
        return conn_schedule

    def schedule_csv_to_db(self, name, init=False): # use this only once for the initial database
        filename = name + '.csv'
        conn = self.get_db_connection('schedule')
        cursor = conn.cursor()

        # write csv to database
        if (init): cursor.execute('DELETE FROM schedule')  # delete contents to avoid doubles
        with open('data/' + filename, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for data in reader:
                data[3], data[4] = self.hour_to_date(int(data[4]))
                data[2] = self.field_number_to_letter(int(data[2]))
                cursor.execute('INSERT INTO schedule(day, teamA, teamB, starttime, field) VALUES (?,?,?,?,?)',
                            (data[3], data[0], data[1], data[4], data[2]))
            conn.commit()
            conn.close()

    # Update the schedule database based on the 'new matches' csv
    # Write match to calendar
    # Write match to database
    def update_tournament_db(self):
        if path.exists('new_match.csv'):
            self.schedule_csv_to_db('new_match') # add data to database
            with open('data/new_match.csv', 'r') as csv_file:
                reader = csv.reader(csv_file)
                for data in reader:
                    data[3], data[4] = self.hour_to_date(int(data[4]))
                    data[2] = self.field_number_to_letter(int(data[2]))
                    self.calHandler.write_event_to_calendar(teamA=data[0], teamB=data[1], field=data[2],
                                                            date=data[3], time=data[4], type='match')
            # remove new_match
            os.remove('new_match.csv')

        else:
            return

    def export_schedule_to_csv(self):
        filename = 'schedule_updated.csv'
        writer = csv.writer(open('data/' + filename, 'w'))
        conn = self.get_db_connection('schedule')
        cursor = conn.cursor()
        data = cursor.execute('SELECT * FROM schedule').fetchall()
        for row in data:
            date = row['day']
            time = row['starttime']
            field = self.field_letter_to_number(row['field'])
            day, hour = self.date_to_hour(date + ' ' + time)
            writer.writerow([row['teamA'], row['teamB'], field, day, hour, row['scoreTeamA'], row['scoreTeamB']])

    def update_team_availability(self, name, init=False):
        if (init):
            # set base availability for all teams
            base = list(csv.reader(open('data/team_availability_base.csv', 'r')))
            csv.writer(open('data/team_availability.csv', 'w')).writerows(base)
            csv.writer(open('data/team_availability_copy.csv', 'w')).writerows(base)

        # write matches from file to team_availability
        reader_file = csv.reader(open('data/' + name + '.csv', 'r'))
        reader_availability = csv.reader(open('data/team_availability_copy.csv', 'r'))
        writer = csv.writer(open('data/team_availability.csv', 'w'))

        availability = list(reader_availability)

        for data in reader_file:
            # set team availability to zero because they have to play a match
            availability[self.team_names_to_row[data[0]]][int(data[4]) + 1] = 0
            availability[self.team_names_to_row[data[1]]][int(data[4]) + 1] = 0

        writer.writerows(availability)

        # copy new availability to the copied file
        csv.writer(open('data/team_availability_copy.csv', 'w')).writerows(availability)