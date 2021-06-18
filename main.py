import json
import threading
from datetime import datetime

from flask import Flask, render_template, request, url_for, flash, redirect
from waitress import serve
from subprocess import Popen, PIPE

from CommunicationHandler import CommunicationHandler
from DataHandler import DataHandler

app = Flask(__name__)
app.config["DEBUG"] = False
app.config['SECRET_KEY'] = 'blah'

dataHandler = DataHandler()
commHandler = CommunicationHandler()

# Initialise database and availability
#dataHandler.update_team_availability(name='schedule', init=True, type='csv')
#dataHandler.schedule_csv_to_db(name='schedule', init=True)
#process = Popen(['data/ssl-scheduling/data/reset.sh'], stdout=PIPE, stderr=PIPE)
#stdout, stderr = process.communicate()
#print(stdout)
#print(stderr)
#process.wait()


###############################################################
############################ HOME #############################
###############################################################
@app.route('/', methods=['GET', 'POST'])
def index():
    # homepage
    print('[index]')
    return render_template('home.html')


###############################################################
###################### TOURNAMENT JSON ########################
###############################################################
@app.route('/tournament_json', methods=['GET'])
def tournament_json():
    # tournament, results and referees in json format
    print('[tournament_json]')
    conn = dataHandler.get_db_connection('schedule')
    cursor = conn.cursor()
    schedule = cursor.execute('SELECT day, starttime, field, referee FROM schedule').fetchall()
    conn.close()
    return json.dumps([dict(ix) for ix in schedule])


###############################################################
######################### TOURNAMENT ##########################
###############################################################
@app.route('/tournament_overview', methods=['GET'])
def tournament():
    # overview of the tournament in table format
    print('[tournament_overview]')
    conn = dataHandler.get_db_connection('schedule')
    schedule = conn.execute('SELECT * FROM schedule ORDER BY day, starttime').fetchall()
    conn.close()
    return render_template('tournament_overview.html', schedule=schedule)


###############################################################
########################### RESULTS ###########################
###############################################################
@app.route('/results', methods=['GET', 'POST'])
def results():
    # form where teams can fill in the results of the match
    print('[results]')
    conn = dataHandler.get_db_connection('schedule')
    cursor = conn.cursor()

    if (request.method == 'POST'):
        team_a      = request.form['team_a']
        team_b      = request.form['team_b']
        date        = request.form['date']
        starttime   = request.form['time']
        score_a     = request.form['score_a']
        score_b     = request.form['score_b']

        print('[main][results] Got results for', team_a, '-', team_b, 'at', date, '', starttime)

        # check if combination of data exists
        cursor.execute(
            'SELECT rowid FROM schedule WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ? AND scoreTeamA IS NULL AND scoreTeamB IS NULL',
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
        # elif (datetime.now () < datetime.strptime(date + ' ' + starttime, '%Y-%m-%d %H:%M')):
        #     flash('This game has not yet started!')
        elif len(rows) == 0:
            flash('Match does not exist or score is already set')
        else: # send to 'check the results' page
            return redirect(url_for('check_results', team_a=team_a, team_b=team_b, date=date,
                                    starttime=starttime, score_a=score_a, score_b=score_b))

    return render_template('results.html')


@app.route('/check_results', methods=['GET', 'POST'])
def check_results():
    # make sure that the results are correctly implemented
    print('[check_results]')
    team_a      = request.args['team_a']
    team_b      = request.args['team_b']
    date        = request.args['date']
    starttime   = request.args['starttime']
    score_a     = request.args['score_a']
    score_b     = request.args['score_b']

    # can be left out but is here for clarity; cancel puts you back to the form
    if (request.method == 'POST') and (request.form['submit'] == 'cancel'):
        return render_template('results.html')

    # put the results in the database
    if (request.method == 'POST') and (request.form['submit'] == 'submit'):
        conn = dataHandler.get_db_connection('schedule')
        # find row where the score must be implemented
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE schedule SET scoreTeamA = ?, scoreTeamB = ? WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ?',
            (score_a, score_b, team_a, team_b, starttime, date))
        conn.commit()
        conn.close()
        commHandler.new_match_results = True
        return redirect(url_for('tournament')) # send back to tournament overview

    return render_template('check_results.html', team_a=team_a, team_b=team_b, date=date,
                           starttime=starttime, score_a=score_a, score_b=score_b)


###############################################################
######################### FRIENDLIES ##########################
###############################################################
@app.route('/request_friendly', methods=['GET', 'POST'])
def request_friendly():
    # form where teams can request a friendly match
    print('[request_friendly]')
    if request.method == 'POST':
        team_a      = request.form['team_a']
        team_b      = request.form['team_b']
        date        = request.form['date']
        starttime   = request.form['time']

        # send a warning if something is missing
        if not team_a:
            flash('Team A is required!')
        elif not team_b:
            flash('Team B is required!')
        elif not date:
            flash('Date is required!')
        elif not starttime:
            flash('Time is required!')
        # elif (datetime.now() < datetime.strptime('2021-06-21 00:00', '%Y-%m-%d %H:%M')):
        #     flash('You can only request friendlies after 21-06-2021!')
        else:
            return redirect(url_for('check_friendly', team_a=team_a, team_b=team_b, date=date, starttime=starttime))

    return render_template('request_friendly.html')


@app.route('/check_friendly', methods=['GET', 'POST'])
def check_friendly():
    print('[check_friendly]')
    team_a      = request.args['team_a']
    team_b      = request.args['team_b']
    date        = request.args['date']
    starttime   = request.args['starttime']

    # can be left out but is here for clarity; cancel puts you back to the form
    if (request.method == 'POST') and (request.form['submit'] == 'cancel'):
        return render_template('request_friendly.html')

    # put the results in the database
    if (request.method == 'POST') and (request.form['submit'] == 'submit'):
        # insert request in friendly database
        conn = dataHandler.get_db_connection('friendlies')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO friendlies (day, teamA, teamB, starttime, status, timestamp) VALUES (?,?,?,?,?,?)',
         (date, team_a, team_b, starttime, 'Pending', datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('request_overview'))

    return render_template('check_friendly.html', team_a=team_a, team_b=team_b, date=date,
                           starttime=starttime)


@app.route('/request_overview', methods=['GET'])
def request_overview():
    print('[request_overview]')
    conn = dataHandler.get_db_connection('friendlies')
    friendly_requests = conn.execute('SELECT * FROM friendlies').fetchall()
    conn.close()
    return render_template('request_overview.html', friendlies=friendly_requests)


###############################################################
########################### REFEREE ###########################
###############################################################
@app.route('/replace_referee', methods=['GET', 'POST'])
def replace_referee():
    print('[replace_referee]')

    conn = dataHandler.get_db_connection('schedule')
    cursor = conn.cursor()

    if request.method == 'POST':
        team_a      = request.form['team_a']
        team_b      = request.form['team_b']
        date        = request.form['date']
        starttime   = request.form['time']
        newref1     = request.form['newref1']
        newref2     = request.form['newref2']

        # check if combination of data exists
        rows = cursor.execute(
            'SELECT rowid FROM schedule WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ?',
            (team_a, team_b, starttime, date)).fetchall()

        # send a warning if something is missing
        if not team_a:
            flash('Team A is required!')
        elif not team_b:
            flash('Team B is required!')
        elif not date:
            flash('Date is required!')
        elif not starttime:
            flash('Time is required!')
        elif not newref1:
            flash('Primary referee is required!')
        elif not newref2:
            flash('Seconday referee is required!')
        elif len(rows) == 0:
            flash('Match does not exist')
        else:
            return redirect(url_for('check_referee', team_a=team_a, team_b=team_b, date=date, starttime=starttime, newref1=newref1, newref2=newref2))


    return render_template('replace_referee.html')


@app.route('/check_referee', methods=['GET', 'POST'])
def check_referee():
    print('[check_referee]')

    team_a      = request.args['team_a']
    team_b      = request.args['team_b']
    date        = request.args['date']
    starttime   = request.args['starttime']
    newref1     = request.args['newref1']
    newref2     = request.args['newref2']

    # can be left out but is here for clarity; cancel puts you back to the form
    if (request.method == 'POST') and (request.form['submit'] == 'cancel'):
        return render_template('replace_referee.html')

    # put the new referees in the database
    if (request.method == 'POST') and (request.form['submit'] == 'submit'):
        conn = dataHandler.get_db_connection('schedule')
        cursor = conn.cursor()

        # retrieve previous referees
        cursor.execute(
            'SELECT referee FROM schedule WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ?',
            (team_a, team_b, starttime, date))
        for row in cursor.fetchone():
            oldref = row

        # update availability of old and new referees
        oldref1, oldref2 = oldref.split(", ")
        day,hour = dataHandler.date_to_hour(date + ' ' + starttime)
        dataHandler.update_team_availability(type='oldref', init=False, name='None', data=[oldref1, hour])
        dataHandler.update_team_availability(type='oldref', init=False, name='None', data=[oldref2, hour])
        dataHandler.update_team_availability(type='ref', init=False, name='None', data=[newref1, hour])
        dataHandler.update_team_availability(type='ref', init=False, name='None', data=[newref2, hour])

        # update referee counters
        dataHandler.update_referee_counter(team=oldref1, type='old_first')
        dataHandler.update_referee_counter(team=oldref2, type='old_first')
        dataHandler.update_referee_counter(team=newref1, type='first')
        dataHandler.update_referee_counter(team=newref2, type='second')

        # insert new referees in schedule database
        cursor.execute(
            'UPDATE schedule SET referee = ? WHERE teamA = ? AND teamB = ? AND starttime = ? AND day = ?',
            (newref1 + ', ' + newref2, team_a, team_b, starttime, date))
        conn.commit()
        conn.close()
        return redirect(url_for('tournament'))

    return render_template('check_referee.html', team_a=team_a, team_b=team_b, date=date,
                           starttime=starttime, newref1=newref1, newref2=newref2)

###############################################################
############################# RUN #############################
###############################################################
update_thread = threading.Thread(target=commHandler.update)
update_thread.start()

serve(app, host="0.0.0.0", port=5000)
update_thread.join()
