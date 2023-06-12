# Author: Aaron Alakkadan 
from app.extensions import db
from app.models.user import User
from app.models.course import Course, Subject
from sqlalchemy.orm import relationship

'''
This is the StudyInterest class model which we inherits from the db.Model class. This represents the StudyInterest table.  
'''
class StudyInterest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    pro_ans1 = db.Column(db.Integer, nullable=False, default=0)
    pro_ans2 = db.Column(db.Integer, nullable=False, default=0)
    pro_ans3 = db.Column(db.Integer, nullable=False, default=0)
    pro_score = db.Column(db.Numeric(precision=2, scale=2), nullable=False)
    buddy_status = db.Column(db.String(1), nullable=False, default = 'N')
    buddy_star_rating = db.Column(db.Integer, nullable=False, default=0)


    user = relationship("User")
    course = relationship("Course")

    def __repr__(self):
        return f"<StudyInterest {self.id}, {self.course_id}>"
