# Author: Aaron Alakkadan, Matt Faiola, Talal Hakki
from flask import Blueprint, render_template, url_for, redirect, request, session 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.dashboard import *
from app.models.user import *
from app.models.course import *
from app.models.studyinterest import *
from app.models.buddyrelation import *
from wtforms.fields import StringField, SelectField, RadioField, SelectMultipleField
from wtforms import widgets
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

'''
Custom SelectMultipleField with checkboxes
'''
class SelectMultipleFieldsWithChecks(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

'''
This is the form class for FindBuddy Form
'''
class FindBuddyForm(FlaskForm):
    subject_code = SelectField('Subject Code', validators=[InputRequired()], choices=[])

    prof_select = SelectMultipleFieldsWithChecks('Proficiency Score', validate_choice=False, 
                                                choices=[(4, '4.0 - 5.0 score'), (3, '3.0 - 4.0 score'), (2, '2.0 - 3.0 score'), (1, '1.0 - 2.0 score')], 
                                                render_kw={'class': 'prof_checks'})

    star_select = SelectMultipleFieldsWithChecks('Buddy Stars', validate_choice=False, 
                                                choices=[(4, '4.0 - 5.0 stars'), (3, '3.0 - 4.0 stars'), (2, '2.0 - 3.0 stars'), (1, '1.0 - 2.0 stars'), (0, 'Unrated Buddies')],
                                                render_kw={'class': 'star_checks'})

    buddy_but = SubmitField("Search Buddy")
    
    select_buddy = RadioField(u'Select',
                              validators=[InputRequired()])
        
    select_buddy_but = SubmitField("Select Buddy")

'''
This is form class for FindBuddyConfirmation form 
'''
class FindBuddyConfirmation(FlaskForm):
    msg = "Invitation has been sent, you will be notified when buddy responds" 

'''
This is the form class for Invitation form
'''
class Invitation(FlaskForm):
    accept_buddy_but = SubmitField("Accept Buddy")
    deny_buddy_but = SubmitField("Deny Buddy")

bp = Blueprint('findstudybuddy', __name__, url_prefix='/')

'''
The findBuddy function encapsulates selecting a buddy based on subject selection, proficiency level, and star level.
'''
@bp.route('/findstudybuddy', methods=['GET', 'POST'])
@login_required
def findBuddy():
    form = FindBuddyForm()
    si_all = None
    subject_buddy_status = 'N'
    user = User.query.filter_by(id=current_user.id).first()
    # Get data for only buddy status in N (not sent), S (sent), D(deny).
    # If buddy status is A (accepted) the user should not be see that subject.
    form.subject_code.choices = [("", "")] + [(si.course.id, f'{si.course.subject_code} {si.course.course_number} - {si.course.course_name}') 
                                 for si in StudyInterest.query.filter_by
                                 (user_id=user.id).filter(
                                or_(
                                StudyInterest.buddy_status=='N', 
                                StudyInterest.buddy_status=='S',
                                StudyInterest.buddy_status=='D')).all()]
    
    # if the submit button is clicked, update the database with the form data inputted from the user.
    if form.validate_on_submit:
        br_user_id = form.select_buddy.data
        course_id = form.subject_code.data
        ''' For all the selected proficiency score range boxes or star rating boxes create a list of filters'''
        id_filters = [StudyInterest.user_id != user.id,
                        StudyInterest.course_id==form.subject_code.data]
        prof_filters = []
        star_filters = []
        # if the proficiency form data is of valid type (list) and is not empty, populate the proficiency filters 
        # list from the form data.
        if isinstance(form.prof_select.data, list) and len(form.prof_select.data) > 0:
            for prof in form.prof_select.data:
                prof1 = int(prof) + 1
                prof_filters.append(and_((StudyInterest.pro_score >= int(prof)),(StudyInterest.pro_score <= int(prof1))))

        # if the star selection form data is of valid type (list) and is not empty, populate the star rating filters 
        # list from the form data.        
        if isinstance(form.star_select.data, list) and len(form.star_select.data) > 0:
            for star in form.star_select.data:
                star1 = int(star) + 1
                star_filters.append(and_((StudyInterest.buddy_star_rating >= int(star)),(StudyInterest.buddy_star_rating <= int(star1))))

        # if the proficiency filters are not empty, query the user's study iterest based on the selected course
        # using the filter.
        # if the star filters are not empty, query the user's study interest based on the selected course using
        # the filter.
        if len(prof_filters) > 0 or len(star_filters) > 0:
            if prof_filters and star_filters:
                si_query = StudyInterest.query.filter(
                    and_(*id_filters, (and_(or_(*prof_filters), or_(*star_filters))))            
                    ).options(joinedload(StudyInterest.course)).options(joinedload(StudyInterest.user))
            elif prof_filters:
                si_query = StudyInterest.query.filter(
                    and_(*id_filters, or_(*prof_filters))            
                    ).options(joinedload(StudyInterest.course)).options(joinedload(StudyInterest.user))
            else:
                si_query = StudyInterest.query.filter(
                    and_(*id_filters, or_(*star_filters))            
                    ).options(joinedload(StudyInterest.course)).options(joinedload(StudyInterest.user))
            
        else:
            si_query = StudyInterest.query.filter(
                    and_(*id_filters)                
                    ).options(joinedload(StudyInterest.course)).options(joinedload(StudyInterest.user))
        si_all = si_query.all()
        
        si_subject_blocked = StudyInterest.query.filter(
            and_(StudyInterest.user_id == user.id,
                  StudyInterest.course_id==course_id
                  )                  
                  ).first()
        # if the subject is blocked, then update the buddy status accordingly.
        if si_subject_blocked:
            subject_buddy_status = si_subject_blocked.buddy_status
            
       # if the select buddy button is clicked, query the database to find the Buddy Receiver's selected subject.
        if form.data['select_buddy_but']:
            buddy_receiver_si = StudyInterest.query.filter(
            and_(StudyInterest.user_id == br_user_id, 
                  StudyInterest.course_id==course_id)).first()
            
            #Save data in the model 
            buddy_sender_si = StudyInterest.query.filter(
            and_(StudyInterest.user_id == user.id, 
                  StudyInterest.course_id==course_id)).first()
            buddy_sender_si.buddy_status = 'S'
            buddy_receiver_si.buddy_status = 'S'
                     
            buddy_status = BuddyRelation.query.filter_by(buddy_sender=current_user.id, buddy_receiver=br_user_id, study_interest_id=buddy_receiver_si.id).first()
            # Create Buddy relation with invitation status as Sent
            if not buddy_status:
                buddy_status = BuddyRelation(buddy_sender=current_user.id, buddy_receiver=br_user_id, 
                                        study_interest_id=buddy_receiver_si.id,
                                        invitation_status='S')
            else:
                buddy_status.invitation_status ='S'
            db.session.add(buddy_status)
            db.session.add(buddy_sender_si)
            db.session.commit()
            #Send invitation email to buddy receiver
            br_user = User.query.filter_by(id=br_user_id).first()
            html_msg = email_content_buddy_invitation(
                username=br_user.username,
                first_name=br_user.first_name,
                last_name=br_user.last_name,
                email_confirmation_url=url_for('auth.login', _external=True)
                ) 
            send_email(email_address=br_user.username, msg_html=html_msg, subject=subjectEmailConfirmation)
            
            #render template to a new template return 
            return redirect(url_for('findstudybuddy.findbuddyconfirmation'))
    return render_template('findstudybuddy.html', form=form, si_all=si_all, subject_buddy_status=subject_buddy_status)

'''
The findbuddy confirmation method initialzes the form FindBuddyComfirmation which informs 
the buddy sender that the inviation has been sent 
'''
@bp.route('/findbuddyconfirmation', methods=['GET'])
def findbuddyconfirmation():
    form = FindBuddyConfirmation()
    return render_template('findbuddyconfirmation.html', form=form, msg=form.msg)

'''
The email_content_buddy_inviation method encapsulates the inviation email content that is being sent to the buddy receiver
'''
def email_content_buddy_invitation(username, first_name, last_name, email_confirmation_url):
    url = f"{email_confirmation_url}"
    return render_template('buddyemail.html', username=username, first_name=first_name, last_name=last_name, url=url)

'''
The invitation method encapsulates the business rules the inviation status when the buddy receiver accepts or denies the buddy request
'''
@bp.route('/invitation', methods=['GET', 'POST'])
def invitation():
    form = Invitation()
    br_id = request.args.get("id")
    br = BuddyRelation.query.filter_by(id=int(br_id), buddy_receiver=current_user.id).first()
    if form.validate_on_submit:
        if form.data['accept_buddy_but'] or form.data['deny_buddy_but']:
            email_address = br.sender.username  #br.sender.username
            # If user accepts buddy then send the acceptance email to the buddy who sent the request
            if form.data['accept_buddy_but']:
                acceptance_status = 'A'
                html_msg = email_content_buddy_acceptance(
                username=br.sender.username,
                first_name=br.sender.first_name,
                last_name=br.sender.last_name,
                email_confirmation_url=url_for('auth.login', _external=True)
                ) 
                send_email(email_address=email_address, msg_html=html_msg, subject=subjectEmailConfirmation)
            
            else:
                # If user denies buddy then send the denial email to the buddy who sent the request
                acceptance_status = 'D'
                html_msg = email_content_buddy_deny(
                username=br.sender.username,
                first_name=br.sender.first_name,
                last_name=br.sender.last_name,
                email_confirmation_url=url_for('auth.login', _external=True)
                ) 
                send_email(email_address=email_address, msg_html=html_msg, subject=subjectEmailConfirmation)

            # Query the database to retreive the buddy sender's selected subject. Update the Buddy status, and
            # invitation status and add an entry to the database.
            sender_si = StudyInterest.query.filter_by(user_id=br.buddy_sender, course_id=br.study_interest.course_id).first()
            sender_si.buddy_status = acceptance_status
            br.invitation_status = acceptance_status
            br.study_interest.buddy_status = acceptance_status
            db.session.add(br)
            db.session.add(sender_si)
            db.session.commit()

    return render_template('invitation.html', form=form, br=br)

'''
The email_content_buddy_acceptance method encapsulates the acceptance email content that is being sent to the buddy
who sent the request
'''
def email_content_buddy_acceptance(username, first_name, last_name, email_confirmation_url):
    url = f"{email_confirmation_url}"
    return render_template('buddyacceptance.html', username=username, first_name=first_name, last_name=last_name, url=url)

'''
The email_content_buddy_deny method encapsulates the denial email content that is being sent to the buddy
who sent the request
'''
def email_content_buddy_deny(username, first_name, last_name, email_confirmation_url):
    url = f"{email_confirmation_url}"
    return render_template('buddydeny.html', username=username, first_name=first_name, last_name=last_name, url=url)
