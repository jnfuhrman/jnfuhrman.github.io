# Author: Aaron Alakkadan
import datetime
from app.extensions import db
from app.models.user import User
from app.models.course import Course, Subject
from app.models.studyinterest import StudyInterest
from app.models.buddyrelation import BuddyRelation
from sqlalchemy.orm import relationship

'''
This is the BuddyRating class model which inherits from the db.Model class. This represents the BuddyRating table. 
'''
class BuddyRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buddy_relation_id = db.Column(db.Integer, db.ForeignKey("buddy_relation.id"))
    rating_sender = db.Column(db.Integer, db.ForeignKey("user.id"))
    rating_receiver = db.Column(db.Integer, db.ForeignKey("user.id"))
    rating_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    is_score_improved = db.Column(db.Boolean, nullable=False)
    is_gained_knowledge = db.Column(db.Boolean, nullable=False)
    buddy_rate = db.Column(db.Integer, nullable=False, default=0)
    comment = db.Column(db.Text, nullable=False, default = '')
    is_survey_completed = db.Column(db.Boolean, nullable=False)
    reward_points = db.Column(db.Integer, nullable=False, default=0)
    sender_survey_points = db.Column(db.Integer, nullable=False, default=0)  

    sender = relationship("User", foreign_keys=[rating_sender])
    receiver = relationship("User", foreign_keys=[rating_receiver])
    buddy_relation = relationship("BuddyRelation")

