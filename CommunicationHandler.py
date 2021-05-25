import csv

class CommunicationHandler():
    def __init__(self):
        # Make csv files for sending/receiving friendly requests
        with open('friendly_request.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['code', 'hour'])

    # Send friendly request
    # - Turn new friendly request to csv
    #
    # def send_friendly_request(self):



    # Receive friendly result

    # Send match results