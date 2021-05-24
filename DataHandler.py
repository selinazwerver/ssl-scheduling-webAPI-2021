import sqlite3
# import pydbc


class DataHandler():
    def __init__(self):
        return

    def get_db_connection_schedule(self):
        conn_schedule = sqlite3.connect('schedule_db.db')
        conn_schedule.row_factory = sqlite3.Row
        return conn_schedule

    def get_db_connection_friendlies(self):
        conn_friendlies = sqlite3.connect('friendlies_db.db')
        conn_friendlies.row_factory = sqlite3.Row
        return conn_friendlies

    def export_db_to_csv(self, database):
        if (database == 'schedule'):
            conn = self.get_db_connection_schedule()

        if (database == 'friendlies'):
            conn = self.get_db_connection_friendlies()


