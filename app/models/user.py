# Author: Aaron Alakkadan, Matt Failoa, Talal Hakki
from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

'''
This is the user class model which inherits from the db.Model class. This represents the user table.    
'''
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, default = '')
    last_name  = db.Column(db.String(50), nullable=False, default = '')
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(20), nullable=True, unique=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    phone_number = db.Column(db.String(20), nullable=False, unique=False, default = '')
    about_me = db.Column(db.Text, nullable=False, default = '')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reward_points = db.Column(db.Integer, nullable=False, default=0)
    survey_points = db.Column(db.Integer, nullable=False, default=0)

    '''
    This is a model property which calculates the total reward points
    '''
    @property
    def total_reward_points(self):
        return self.reward_points + self.survey_points

    def __repr__(self):
        return f"<User {self.id}>"

