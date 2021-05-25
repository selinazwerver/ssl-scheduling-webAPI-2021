import csv
from datetime import datetime, timedelta

class CommunicationHandler():
    def __init__(self):  
        self.sending_friendly_request = False
        
        # Make csv files for sending/receiving friendly requests
        with open('friendly_request.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['code', 'hour'])

    def date_to_hour(self, date):
        # Assumes that we start on Monday!
        timestamp = datetime.strptime(date, '%Y-%m-%d %H:%M')
        hour = (timestamp.timetuple().tm_wday*24 + 24) - (24 - timestamp.timetuple().tm_hour)
        return hour

    def hour_to_date(self, hour):
        starttime = datetime.strptime('2021-06-21 00:00', '%Y-%m-%d %H:%M')
        date = starttime + timedelta(hours=hour)
        return date

    def find_oldest_request(self):
        # establish connection
        # conn = ....
        # cursor = conn.cursor()
        # cursor.execute('SELECT min(timestamp) FROM friendlies WHERE status = Pending')
        # rows = cursor.fetchall()
        # conn.commit()
        # conn.close()

        # rows to excel sheet
        return

    # Send friendly request
    # - Turn new friendly request to csv
    #
    def send_friendly_request(self):
        if (self.send_friendly_request == False):
            do_stuff = 1 

    # Receive friendly result
    def receive_friendly_request(self):
        self.send_friendly_request = True

    # Send match results