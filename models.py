import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON


class PersonalData(db.Model):
    __tablename__ = 'personal_data'

    id = db.Column(db.Integer, primary_key=True)
    rescue_time_daily = db.Column(JSON)
    rescue_time_weekly = db.Column(JSON)
    quote = db.Column(db.String(200))
    weight = db.Column(db.Integer)
    chess_rating = db.Column(db.Integer)
    steps = db.Column(db.Integer)
    steps_avg = db.Column(db.Integer)
    pomodoros = db.Column(JSON)
    date = db.Column(db.DateTime)

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.rescue_time_daily = rescue_time_daily
        self.rescue_time_weekly = rescue_time_weekly
        self.quote = quote
        self.weight = weight
        self.chess_rating = chess_rating
        self.steps = steps
        self.steps_avg = steps_avg
        self.pomodoros = pomodoros
        self.date = date

    def __repr__(self):
        return '<id {}>'.format(self.id)
