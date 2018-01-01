import datetime
from app import db
from sqlalchemy import Column, Integer, DateTime, JSON

class GoalCompletion(db.Model):
    __tablename__ = 'dates_completed_goals'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(JSON)

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return '<id {}>'.format(self.id)


class PersonalData(db.Model):
    __tablename__ = 'personal_data'
    id = db.Column(db.Integer, primary_key=True)
    personal_data_dictionary = db.Column(JSON)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, personal_data_dictionary, created_date):
        self.personal_data_dictionary = personal_data_dictionary
        self.created_date = created_date

    def __repr__(self):
        return '<id {}>'.format(self.id)
