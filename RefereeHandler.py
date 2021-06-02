import csv

class RefereeHandler():
    def __init__(self):
        return

    def init_referee_counter(self, teams):
        self.referee_counter = []
        for team in teams:
            self.referee_counter.append([team, 0])
        
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

        lowest_count = 900
        referee = ''
        for team in teams:
            count = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1]
            if count < lowest_count:
                lowest_count = count
                referee = team
        
        self.update_referee_counter(team=referee) 
        return referee


    def update_referee_counter(self, team):
        self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] = self.referee_counter[list(list(zip(*self.referee_counter))[0]).index(team)][1] + 1


