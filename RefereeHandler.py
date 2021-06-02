import csv

class RefereeHandler():
    def __init__(self):
        return

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
        
        self.update_referee_counter(team=second_referee, type='second') 
        
        return first_referee + ', ' + second_referee


    def update_referee_counter(self, team, type):
        if type=='first':
            self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] + 1
        elif type=='second':
            self.second_referee_counter[list(list(zip(*self.second_referee_counter))[0]).index(team)][1] = self.second_referee_counter[list(list(zip(*self.second_referee_counter))[0]).index(team)][1] + 1

