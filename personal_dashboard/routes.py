from flask import Blueprint, render_template, jsonify
from .services.rescuetime import RescueTime
from .services.todoist import Todoist
from .services.spotify import Spotify
from .services.moves import Moves
from .services.chess import Chess
from .services.toggl import Toggl
from .services.meditation import Meditation
from .services.books import Books
from .services.articles import Articles
from .services.quotes import Quote
import requests
import datetime as dt
import time
import threading
import random
import webbrowser

bp = Blueprint('main', __name__)

@bp.route('/')
def hello_world():
    return render_template('index.html')

@bp.route("/data", methods=['GET'])
def data():
    rescue_time = RescueTime()
    spotify = Spotify()
    moves = Moves()
    todoist = Todoist()
    toggl = Toggl()
    quote = Quote()
    meditation = Meditation()
    books = Books()
    articles = Articles()
    chess = Chess()
    wakatime_coding_time = requests.get('https://wakatime.com/share/@0c62f2ad-9fa5-43c7-a08f-7b1562918a7d/43cd4128-5361-43db-b51b-d965e3c575a5.json').json()
    wakatime_coding_type = requests.get('https://wakatime.com/share/@0c62f2ad-9fa5-43c7-a08f-7b1562918a7d/27967d19-0ce0-42a6-9f4a-c3c2440cf575.json').json()

    info = {
        'rescue_time_daily_unproductivity': rescue_time.get_current_days_data()["unproductive_hours"],
        'current_meditation': meditation.get_current_meditation_time(),
        'rescue_time_past_seven_productivity': rescue_time.get_past_seven_days_data()["productive_hours"],
        'rescue_time_past_seven_unproductivity': rescue_time.get_past_seven_days_data()["unproductive_hours"],
        'rescue_time_past_seven_top_five': rescue_time.get_past_seven_days_data()["top_five_sources"],
        'top_tracks': spotify.get_monthly_top_tracks(),
        'top_artists': spotify.get_monthly_top_artists(),
        'quote_content': quote.content,
        'quote_author': quote.author,
        'daily_doughnut_pomodoro': toggl.get_daily_pomodoros(),
        'past_seven_days_pomodoros': toggl.get_past_seven_days_pomodoros(),
        'coding_time': wakatime_coding_time['data'],
        'coding_type': wakatime_coding_type['data'],
        'rescuetime_bar_data': rescue_time.get_daily_week_view()[0],
        'rescuetime_bar_data_dates': rescue_time.get_daily_week_view()[1],
        'toggl_bar_data': toggl.get_daily_week_view(),
        'pomodoro_goal': 2.4,
        'unproductivity_goal': 1,
        'meditation_goal': 20,
        'meditation_data': meditation.get_weekly_meditation_data(),
        'past_books': books.get_past_n_books(3),
        'books_bar_data': books.get_past_reading_history()[0],
        'books_bar_data_dates': books.get_past_reading_history()[1],
        'past_writing': articles.get_past_n_articles(3),
        'writing_bar_data': articles.get_past_n_month_writing_history(6)[0],
        'writing_bar_data_dates': articles.get_past_n_month_writing_history(6)[1],
        'meditation_bar_data': meditation.get_weekly_meditation_data()[0],
        'meditation_bar_data_dates': meditation.get_weekly_meditation_data()[1],
        'top_three_sources': rescue_time.get_current_days_data()["top_three_sources"]
    }
    return jsonify(info)


@bp.route("/updated")
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

def occasional_update(app, minsecs=40, maxsecs=50, first_time=False):
    """
    Simulate the server having occasional updates for the client. The first
    time it's run (presumably synchronously with the main program), it just
    kicks off an asynchronous Timer. Subsequent invocations (via Timer)
    actually signal an update is ready.
    """
    with app.app_context():
        app.config['updated'] = not first_time
        delay = random.randint(minsecs, maxsecs)
        threading.Timer(delay, occasional_update, [app]).start()
