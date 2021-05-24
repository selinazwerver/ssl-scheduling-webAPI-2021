import sqlite3

connection = sqlite3.connect('friendlies.db')

with open('friendlies.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()