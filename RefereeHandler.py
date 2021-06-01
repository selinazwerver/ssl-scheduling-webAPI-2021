from DataHandler import DataHandler

class RefereeHandler():
    def __init__(self):
        self.dataHandler = DataHandler()
        self.init_referee_counter()

    def init_referee_counter(self):
        self.referee_counter = []
        for name in self.dataHandler.team_names_to_row:
            self.referee_counter.append([name, 0])

