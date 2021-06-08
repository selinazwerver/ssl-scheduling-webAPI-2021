import sqlite3
import csv
from datetime import datetime, timedelta
import math
import os
import operator
from os import path
from CalendarHandler import CalendarHandler

class DataHandler():
    def __init__(self):
        self.calHandler = CalendarHandler()

        self.csv_format = {
            'teamA': 0,
            'teamB': 1,
            'field': 2,
            'time': 3

        }

        self.team_names_to_row = {
            'ER-Force': 0,
            'RoboCIn': 1,
            'RoboTeam Twente': 2,
            'KIKS': 3,
            'TIGERs Mannheim': 4,
            'KgpKubs': 5,
            'RoboIME': 6,
            'RoboFEI': 7,
            'UBC Thunderbots': 8,
            'RoboDragons': 9,
            'MRL': 10,
            'RoboJackets': 11,
            'Tritons RCSC': 12,
            'Omid': 13,
            'URoboRus': 14,
            'SRC': 15
        }

        self.init_referee_counter(self.team_names_to_row)

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

        # write csv to database, update calendar
        if (init): cursor.execute('DELETE FROM schedule')  # delete contents to avoid doubles
        with open('data/' + filename, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            sortedreader = sorted(reader, key=lambda row: int(row[self.csv_format['time']]), reverse=False)
            for data in sortedreader:
                referee = self.get_referee(data[self.csv_format['time']]) # get referee for the match
                day, data[self.csv_format['time']] = self.hour_to_date(int(data[self.csv_format['time']]))
                data[self.csv_format['field']] = self.field_number_to_letter(int(data[self.csv_format['field']]))
                cursor.execute('INSERT INTO schedule(day, teamA, teamB, starttime, field, referee) VALUES (?,?,?,?,?,?)',
                            (day, data[self.csv_format['teamA']], data[self.csv_format['teamB']], data[self.csv_format['time']], data[self.csv_format['field']], referee))
                # self.calHandler.write_event_to_calendar(teamA=data[0], teamB=data[1], field=data[2],
                                                            # date=day, time=data[3], referee=referee, type='match')
            conn.commit()
            conn.close()

    def update_tournament_db(self):
        if path.exists('new_match.csv'):
            self.update_team_availability('new_match', type='csv') # update team availability              
            self.schedule_csv_to_db('new_match') # add data to database
            
            # remove new_match
            os.remove('new_match.csv')

        else:
            return

    def export_schedule_to_csv(self):
        filename = 'schedule_updated.csv'
        writer = csv.writer(open('data/' + filename, 'w', newline=''))
        conn = self.get_db_connection('schedule')
        cursor = conn.cursor()
        data = cursor.execute('SELECT * FROM schedule').fetchall()
        for row in data:
            date = row['day']
            time = row['starttime']
            field = self.field_letter_to_number(row['field'])
            day, hour = self.date_to_hour(date + ' ' + time)
            writer.writerow([row['teamA'], row['teamB'], field, day, hour, row['scoreTeamA'], row['scoreTeamB']])

    def update_team_availability(self, type, init=False, name='None', data=[]):
        if (init == True):
            # set base availability for all teams
            base = list(csv.reader(open('data/team_availability_base.csv', 'r'), delimiter=','))
            csv.writer(open('data/team_availability.csv', 'w', newline='')).writerows(base)
            csv.writer(open('data/team_availability_copy.csv', 'w', newline='')).writerows(base)

        # write matches from file to team_availability
        reader_availability = csv.reader(open('data/team_availability_copy.csv', 'r'), delimiter=',')
        writer = csv.writer(open('data/team_availability.csv', 'w', newline=''))

        availability = list(reader_availability)

        if (type=='csv'):
            reader_file = csv.reader(open('data/' + name + '.csv', 'r'), delimiter=',')
            for row in reader_file:
                # set team availability to zero because they have to play a match
                availability[self.team_names_to_row[row[self.csv_format['teamA']]]][int(row[self.csv_format['time']]) + 1] = 0
                availability[self.team_names_to_row[row[self.csv_format['teamB']]]][int(row[self.csv_format['time']]) + 1] = 0
        elif (type=='list'):
            availability[self.team_names_to_row[data[0]]][int(data[2]) + 1] = 0
            availability[self.team_names_to_row[data[1]]][int(data[2]) + 1] = 0
        elif (type=='ref'):
            availability[self.team_names_to_row[data[0]]][int(data[1]) + 1] = 0
        

        writer.writerows(availability)

        # copy new availability to the copied file
        csv.writer(open('data/team_availability_copy.csv', 'w', newline='')).writerows(availability)




    # REFEREE STUFF
    def init_referee_counter(self, teams):
        self.referee_counter = []
        self.second_referee_counter = []
        for team in teams:
            self.referee_counter.append([team, 0])
            self.second_referee_counter.append([team, 0])
        
    def find_available_teams(self, hour):
        reader = csv.reader(open('data/team_availability.csv', 'r'), delimiter=',')
        availability = list(reader)
        available_teams = []
        for row in availability:
            if int(row[int(hour)+1]) == 1:
                available_teams.append(row[0])
        
        return available_teams

    def get_referee(self, hour):
        teams = self.find_available_teams(hour=hour)

        if len(teams) == 0:
            return 'OC, TC'

        lowest_count = 900 # arbitraty high number
        first_referee = ''
        for team in teams:
            count = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1]
            if count < lowest_count:
                lowest_count = count
                first_referee = team

        self.update_team_availability(type='ref', data=[first_referee, hour])
        self.update_referee_counter(team=first_referee, type='first') 

        if len(teams) == 1:
            return first_referee + ', OC'

        # remove first referee from options and determine second
        teams.remove(first_referee)

        lowest_count = 900
        second_referee = ''
        for team in teams:
            count = self.second_referee_counter[list(list(zip(*self.second_referee_counter))[0]).index(team)][1]
            if count < lowest_count:
                lowest_count = count
                second_referee = team
        
        self.update_team_availability(type='ref', data=[second_referee, hour])
        self.update_referee_counter(team=second_referee, type='second') 
        
        return first_referee + ', ' + second_referee


    def update_referee_counter(self, team, type):
        if type=='first':
            self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] + 1
        elif type=='second':
            self.second_referee_counter[list(list(zip(*self.second_referee_counter))[0]).index(team)][1] = self.second_referee_counter[list(list(zip(*self.second_referee_counter))[0]).index(team)][1] + 1
