# Author: Aaron Alakkadan
import datetime
from app.extensions import db
from app.models.user import User
from app.models.course import Course, Subject
from app.models.studyinterest import StudyInterest
from app.models.buddyrelation import BuddyRelation
from sqlalchemy.orm import relationship

'''
This is the Document class model which inherits from the db.Model class. This represents the Document table.
'''
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buddy_sender = db.Column(db.Integer, db.ForeignKey("user.id"))
    buddy_receiver = db.Column(db.Integer, db.ForeignKey("user.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    date_uploaded = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comment = db.Column(db.String(50), nullable=False, default = '')
    name = db.Column(db.String(50), nullable=False, default = '')
    content = db.Column(db.LargeBinary())
    

    sender = relationship("User", foreign_keys=[buddy_sender])
    receiver = relationship("User", foreign_keys=[buddy_receiver])
    course = relationship("Course")
    
