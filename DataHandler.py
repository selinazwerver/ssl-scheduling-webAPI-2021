import sqlite3
import csv

class DataHandler():
    def __init__(self):
        return

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
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(cursor)


