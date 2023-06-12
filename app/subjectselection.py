# Author: Aaron Alakkadan, Matt Faiola 
from flask import Blueprint, render_template, url_for, redirect, request, session, jsonify 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from wtforms.fields import StringField, SelectField, RadioField
from app.auth import *
from app.dashboard import *
from app.models.course import *
from app.models.studyinterest import *
from statistics import mean
from sqlalchemy.orm import joinedload

'''
This is the form class for subject selection
'''
class SubjectSelectionForm(FlaskForm):
    subject_code = SelectField('Subject Code', validators=[InputRequired()], choices=[])

    course_title = SelectField('Course Title', validators=[InputRequired()], choices=[], 
                               render_kw={"onchange": "course_title.onchange()"})

    pro_ans1 = RadioField(u'How Knowledgeable are you on a subject?',
                          validators=[InputRequired()],
                           choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")])
    pro_ans2 = RadioField(u'What is your Current Grade in this subject?',
                          validators=[InputRequired()], 
                           choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")])
    pro_ans3 = RadioField(u'How would you Rate Yourself in this subject?',
                          validators=[InputRequired()], 
                           choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")])   
    but = SubmitField("Submit")

'''
This is the form class for Subject Deletion 
'''
class SubjectDeleteForm(FlaskForm):
    subject_remove = SelectField('Subject Code', validators=[InputRequired()], choices=[], render_kw={"onchange": "subject_delete.onchange()"})
    delbut = SubmitField("Remove Subject From List")

'''
The calc_pro_score function encapsulates calculation the proficiency score based on the three profiency answers
The function returns the average of the three answers which the user answers on a scale from 1-5.
'''
def calc_pro_score(form):
    return round(mean([int(form.pro_ans1.data),
                                     int(form.pro_ans2.data), 
                                     int(form.pro_ans3.data)]),2)

bp = Blueprint('subjectselection', __name__, url_prefix='/')

'''
The subjectSelection function ensacpautes a user selecting and deleting subjects
'''
@bp.route('/subjectselection', methods=['GET', 'POST'])
@login_required
def subjectSelection():
    form = SubjectSelectionForm()
    form_delete = SubjectDeleteForm()
    form.subject_code.choices = [(Subject.subject_code, f'{Subject.subject_code} - {Subject.subject_name}') for Subject in Subject.query.all()]
    user = User.query.filter_by(username=current_user.username).first()
    form_delete.subject_remove.choices = [(StudyInterest.course_id, f'({StudyInterest.course.subject_code}) - {StudyInterest.course.course_number} - {StudyInterest.course.course_name}') for StudyInterest in StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()]
    course = None
    si_all = None
    si = None
    # if the user decides to delete a subject and confirms via button click, query the selected subject and remove the
    # entry from the database. Commit changes to database.
    if form_delete.validate_on_submit:
        if user:
            if form_delete.data['delbut']:
                course_id  = form_delete.subject_remove.data

                total_si = StudyInterest.query.filter_by(user_id=user.id).count()
                if total_si <= 0:
                    msg_delete = "No subjects to remove"
                    return render_template('subjectselection.html', form=form, form_delete=form_delete, course=course, si_all=si_all, msg_delete=msg_delete)
                si = StudyInterest.query.filter_by(user_id=user.id).filter_by(course_id=form_delete.subject_remove.data).first()
                db.session.query(StudyInterest).filter(StudyInterest.id == si.id).delete()
                db.session.commit()
                form_delete.subject_remove.data = None
                si_all = StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()
                form_delete.subject_remove.choices = [(StudyInterest.course_id, f'({StudyInterest.course.subject_code}) - {StudyInterest.course.course_number} - {StudyInterest.course.course_name}') for StudyInterest in StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()]

    # if the user decides to add a subject and confirms via button click, query the selected subject and add an
    # entry to the database. Commit changes to database.
    if form.validate_on_submit:
        if user:
            si_all = StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()
            if form.data['but']:
                #Count si study_interest
                course_id  = form.course_title.data # Option value contains id 
                course = Course.query.filter_by(id=course_id).first()
                total_si = StudyInterest.query.filter_by(user_id=user.id).count()
                
                # if the user has hit the subject limit of 5, display an error message.
                if total_si >= 5:
                    msg = "Maximum number of subjects selected"
                    return render_template('subjectselection.html', form=form, form_delete=form_delete, course=course, si_all=si_all, msg=msg)
                
                si = StudyInterest.query.filter_by(user_id=user.id).filter_by(course_id=course.id).first()
                # update the proficiency score answers using the form data and calculate the average.
                if si:
                    si.pro_ans1 = form.pro_ans1.data
                    si.pro_ans2 = form.pro_ans2.data
                    si.pro_ans3 = form.pro_ans3.data
                    si.pro_score = calc_pro_score(form)
                                                   
                else:
                    si = StudyInterest(user_id=user.id, course_id=course.id, pro_ans1=form.pro_ans1.data,
                               pro_ans2=form.pro_ans2.data, pro_ans3=form.pro_ans3.data, 
                               pro_score= calc_pro_score(form))
                                    
                db.session.add(si)
                db.session.commit()
                form.subject_code.data = None
                form.course_title.data = None
                form.pro_ans1.data = None
                form.pro_ans2.data = None
                form.pro_ans3.data = None
            si_all = StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()
            form_delete.subject_remove.choices = [(StudyInterest.course_id, f'({StudyInterest.course.subject_code}) - {StudyInterest.course.course_number} - {StudyInterest.course.course_name}') for StudyInterest in StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()]
    return render_template('subjectselection.html', form=form, form_delete=form_delete, course=course, si_all=si_all)
 
'''
The codesortcourse function is used to populate the course title dropdown list based on the subject code selected
This code handles requests to "/subjectselection/<get_code>" which isnt shown to the user.
It queries the database for all courses that match the given subject code, creates an array of those courses, 
and returns the array in JSON format
'''

@bp.route('/subjectselection/<get_code>', methods=['GET', 'POST'])
@login_required
def codesortcourse(get_code):
    course = Course.query.filter_by(subject_code=get_code).all()
    course_array = [{"id" : "", "code" : "", "number" : "", "name" : "Select a Course Title"}]
    for code in course:
        course = {}
        course['id'] = code.id
        course['code'] = code.subject_code
        course['number'] = code.course_number
        course['name'] = code.course_name
        course_array.append(course)
    return jsonify({'courselist': course_array})
