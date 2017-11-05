import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON

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


    def __init__(self, personal_data_dictionary):
        self.personal_data_dictionary = personal_data_dictionary

    def __repr__(self):
        return '<id {}>'.format(self.id)
