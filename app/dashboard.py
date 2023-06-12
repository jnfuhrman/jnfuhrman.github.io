# Author: Aaron Alakkadan, Talal Hakki, and Matt Faiola 
from flask import Blueprint, render_template, url_for, redirect, request, session 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.models.studyinterest import *
from app.models.buddyrelation import *
from sqlalchemy.orm import joinedload
from sqlalchemy import and_ , or_

'''
This is the form class for the Dashboard
'''
class DashboardForm(FlaskForm):
    findBuddyBut = SubmitField("Buddy Search")
    subjectSelBut = SubmitField("Subject Select")
    matViewBut = SubmitField("View Materials")
    viewRateBut = SubmitField("View Ratings")
    profileBut = SubmitField("Profile")
    logoutBut = SubmitField("Logout")

'''
Create the blueprint for dashboard
'''
bp = Blueprint('dashboard', __name__, url_prefix='/')

'''
The dashboard function encapsulates all business rules for dashboard features.

The dashboard function checks if the user clicks a button on the navigation bar in the dashboard then it will redirect to
the corresponding or respective page.
'''
@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = DashboardForm()
    if form.validate_on_submit(): 
        if form.data['findBuddyBut']:
            return redirect(url_for('findstudybuddy.findBuddy'))  

        elif form.data['subjectSelBut']:
            return redirect(url_for('subjectselection.subjectSelection')) 

        elif form.data['matViewBut']:
            return redirect(url_for('materialsview.materialsView'))

        elif form.data['viewRateBut']:
            return redirect(url_for('viewratings.viewRatings'))

        elif form.data['profileBut']:
            return redirect(url_for('profile.profile'))
        
        elif form.data['logoutBut']:
            return redirect(url_for('auth.login'))

    # query the user table to find the current user to retrieve all subjects from their subject list
    # and buddy connections to display on the dashboard.
    si_all = None
    user = User.query.filter_by(username=current_user.username).first()
    if user:
        si_all = StudyInterest.query.filter_by(user_id=user.id).options(joinedload(StudyInterest.course)).all()
        br = BuddyRelation.query.filter_by(buddy_receiver=user.id, invitation_status='S')
        br_connections = BuddyRelation.query.filter(or_(BuddyRelation.buddy_receiver==user.id, BuddyRelation.buddy_sender==user.id), BuddyRelation.invitation_status=='A').all()
    else:
        print("********")
        print(current_user.username)
    return render_template('dashboard.html', form=form, si_all=si_all, br=br, br_connections=br_connections, user=user)


   



    