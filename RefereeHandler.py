from DataHandler import DataHandler
import csv

class RefereeHandler():
    def __init__(self):
        self.dataHandler = DataHandler()
        self.init_referee_counter()

    def init_referee_counter(self):
        self.referee_counter = []
        for name in self.dataHandler.team_names_to_row:
            self.referee_counter.append([name, 0])

    def find_available_teams(self, hour):
        reader = csv.reader(open('data/team_availability.csv', 'r'), delimiter=',')
        availability = list(reader)
        available_teams = []
        for row in availability:
            if int(row[hour+1]) == 1:
                available_teams.append(row[0])
        
        return available_teams

    def choose_referee(self, teams):
        lowest_count = 900
        referee = ''
        for team in teams:
            count = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1]
            if count < lowest_count:
                referee = team
        
        self.update_referee_counter(team=referee) 
        return referee


    def update_referee_counter(self, team):
        self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] + 1


