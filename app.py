# from personal_dashboard.mint import Mint
from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify
import time, threading, random, webbrowser
from personal_dashboard.bus_directions import NextBus
from personal_dashboard.quotes import QUOTE
from flask import send_from_directory
from personal_dashboard.rescuetime import RescueTime
from personal_dashboard.withings import Withings
from personal_dashboard.todoist import Todoist
from personal_dashboard.spotify import Spotify
from personal_dashboard.darksky import DarkSky
from personal_dashboard.moves import Moves
from personal_dashboard.chess import Chess
from personal_dashboard.toggl import Toggl
import psycopg2

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


@app.route('/')
def hello_world():
    return render_template('index.html', quote=QUOTE)


@app.route("/data", methods=['GET'])
def data():
    """
    Primary data source for AJAX/REST queries. Gets the server's current
    time two ways: as raw data, and as a formatted string. NB While other
    Python JSON emitters will directly encode arrays and other data types,
    Flask.jsonify() appears to require a dict.
    """
    time.sleep(10)
    rescue_time = RescueTime()
    # next_bus = NextBus().get_next_bus()
    withings = Withings()
    todoist = Todoist()
    spotify = Spotify()
    darksky = DarkSky()
    moves = Moves()
    chess = Chess()
    toggl = Toggl()
    info = { 'rescue_time_daily_productivity': rescue_time.get_current_days_data()["productive_hours"],
            'rescue_time_daily_unproductivity' : rescue_time.get_current_days_data()["unproductive_hours"],
            'rescue_time_daily_top_three' :  rescue_time.get_current_days_data()["top_three_sources"],
            'rescue_time_past_seven_productivity' : rescue_time.get_past_seven_days_data()["productive_hours"],
            'rescue_time_past_seven_unproductivity' : rescue_time.get_past_seven_days_data()["unproductive_hours"],
            'rescue_time_past_seven_top_five' : rescue_time.get_past_seven_days_data()["top_five_sources"],
            'quote' : QUOTE,
            # 'next_bus' : next_bus,
            'weight' : withings.weight,
            'total_tasks' : todoist.get_total_tasks(),
            'past_seven_completed_tasks' : todoist.get_past_seven_completed_tasks(),
            'daily_completed_tasks' : todoist.get_daily_completed_tasks(),
            'top_tracks' : spotify.get_monthly_top_tracks(),
            'top_artists' : spotify.get_monthly_top_artists(),
            'weather_hourly' : darksky.weather_hourly,
            'temp' : darksky.temp,
            'weather_today' : darksky.weather_today,
            'current_steps' : moves.get_current_days_steps(),
            'average_past_seven_steps' : moves.get_average_past_seven_steps(),
            'chess_rating' : chess.get_games(),
            'chess_games' : chess.get_rating(),
            'daily_pomodoros' : str(toggl.get_daily_pomodoros()),
            'past_seven_days_pomodoros' : str(toggl.get_past_seven_days_pomodoros())
            }
    return jsonify(info)


@app.route("/updated")
def updated():
    """
    Wait until something has changed, and report it. Python has *meh* support
    for threading, as witnessed by the umpteen solutions to this problem (e.g.
    Twisted, gevent, Stackless Python, etc). Here we use a simple check-sleep
    loop to wait for an update. app.config is handy place to stow global app
    data.
    """
    time.sleep(10)
    return "changed!"


def occasional_update(minsecs=40, maxsecs=50, first_time=False):
    """
    Simulate the server having occasional updates for the client. The first
    time it's run (presumably synchronously with the main program), it just
    kicks off an asynchronous Timer. Subsequent invocations (via Timer)
    actually signal an update is ready.
    """
    app.config['updated'] = not first_time
    delay = random.randint(minsecs, maxsecs)
    threading.Timer(delay, occasional_update).start()


if __name__ == "__main__":
    # start occasional update simulation
    occasional_update(first_time=True)
    app.run(threaded=True)
    # start server and web page pointing to it
    # url = "http://127.0.0.1:{}".format(port)
    # wb = webbrowser.get(None)  # instead of None, can be "firefox" etc
    # threading.Timer(1.25, lambda: wb.open(url) ).start()
    app.run(debug=True)
