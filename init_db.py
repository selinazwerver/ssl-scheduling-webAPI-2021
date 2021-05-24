import sqlite3

connection = sqlite3.connect('schedule.db')

with open('schedule.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO schedule (day, teamA, teamB, starttime) VALUES (?,?,?,?)",
            ('2021-06-15', 'RoboTeam Twente', 'ER-Force', '14:00')
            )

cur.execute("INSERT INTO schedule (day, teamA, teamB, starttime) VALUES (?,?,?,?)",
            ('2021-06-16', 'TIGERs Mannheim', 'ER-Force', '14:00')
            )

connection.commit()
connection.close()