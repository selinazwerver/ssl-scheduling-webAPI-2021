from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from datetime import datetime
from DataHandler import DataHandler
from CommunicationHandler import CommunicationHandler

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'blah'

dataHandler = DataHandler()
commHandler = CommunicationHandler()

# TestsS
# commHandler.date_to_hour('2021-06-22 14:00')
# commHandler.hour_to_date(38)
# dataHandler.export_db_to_csv('schedule')
# dataHandler.export_csv_to_db('schedule')
# dataHandler.export_db_to_csv('schedule')
# commHandler.convert_db_to_normal_time('schedule')
commHandler.send_friendly_request()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home.html')

@app.route('/tournament_overview', methods = ['GET'])
def tournament():
    conn = dataHandler.get_db_connection('schedule')
    schedule = conn.execute('SELECT * FROM schedule').fetchall()
    conn.close()
    return render_template('tournament_overview.html', schedule = schedule)

@app.route('/results', methods = ['GET', 'POST'])
def results():
    conn = dataHandler.get_db_connection('schedule')
    cursor = conn.cursor()

    if (request.method == 'POST'):
        team_a = request.form['team_a']
        team_b = request.form['team_b']
        date = request.form['date']
        starttime = request.form['time']
        score_a = request.form['score_a']
        score_b = request.form['score_b']

        # check if combination of data exists
        cursor.execute('SELECT rowid FROM schedule WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ?',
                       (team_a, team_b, starttime, date))
        rows = cursor.fetchall()

        # send a warning if something is missing
        if not team_a:
            flash('Team A is required!')
        elif not team_b:
            flash('Team B is required!')
        elif not date:
            flash('Date is required!')
        elif not starttime:
            flash('Time is required!')
        elif not score_a:
            flash('Score of Team A is required!')
        elif not score_b:
            flash('Score of Team B is required!')
        elif len(rows) == 0:
            flash('Match does not exist!')
        else:
            return redirect(url_for('check_results', team_a=team_a, team_b=team_b, date=date,
                            starttime=starttime, score_a=score_a, score_b=score_b))

    return render_template('results.html')

@app.route('/check_results', methods=['GET', 'POST'])
def check_results():
    # parsing as function arguments was apparently not ok
    team_a = request.args['team_a']
    team_b = request.args['team_b']
    date = request.args['date']
    starttime = request.args['starttime']
    score_a = request.args['score_a']
    score_b = request.args['score_b']

    # can be left out but is here for clarity; cancel puts you back to the form
    if (request.method == 'POST') and (request.form['submit'] == 'cancel'):
        return render_template('results.html')

    # put the results in the database
    if (request.method == 'POST') and (request.form['submit'] == 'submit'):
        conn = dataHandler.get_db_connection('schedule')
        # find row where the score must be implemented
        cur = conn.cursor()
        cur.execute('UPDATE schedule SET scoreTeamA = ?, scoreTeamB = ? WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ?',
                    (score_a, score_b, team_a, team_b, starttime, date))
        conn.commit()
        conn.close()
        # commHandler.send_match_results()
        return redirect(url_for('tournament'))

    return render_template('check_results.html', team_a=team_a, team_b=team_b, date=date,
                            starttime=starttime, score_a=score_a, score_b=score_b)

@app.route('/request_overview', methods = ['GET'])
def request_overview():
    conn = dataHandler.get_db_connection('friendlies')
    friendly_requests = conn.execute('SELECT * FROM friendlies').fetchall()
    conn.close()
    return render_template('request_overview.html', friendlies = friendly_requests)

@app.route('/request_friendly', methods = ['GET', 'POST'])
def request_friendly():
    if request.method == 'POST':
        team_a = request.form['team_a']
        team_b = request.form['team_b']
        date = request.form['date']
        time = request.form['time']

        if not team_a:
            flash('Team A is required!')
        if not team_b:
            flash('Team B is required!')
        if not date:
            flash('Date is required!')
        if not time:
            flash('Time is required!')
        else:
            conn = dataHandler.get_db_connection('friendlies')
            conn.execute('INSERT INTO friendlies (day, teamA, teamB, starttime, status, timestamp) VALUES (?,?,?,?,?,?)',
                         (date, team_a, team_b, time, 'Pending', datetime.now()))
            conn.commit()
            conn.close()
            dataHandler.export_db_to_csv('friendlies')
            return redirect(url_for('request_overview'))

    return render_template('request_friendly.html')

@app.route('/calendar', methods=['GET'])
def calendar():
    return render_template('calendar.html')


app.run()