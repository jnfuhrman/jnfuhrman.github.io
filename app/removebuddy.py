# Author: Talal Hakki, Matt Faiola
from flask import Blueprint, render_template, url_for, redirect, request, session 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.dashboard import *
import flask_login
from app.models.studyinterest import *


'''
This is the form class for the remove buddy class
'''
class RemoveBuddyForm(FlaskForm):
    remove_but = SubmitField("Yes")
    dont_remove_but = SubmitField("No")


bp = Blueprint('removebuddy', __name__, url_prefix='/')

'''
The removeBuddy method encapsulates all business rules for removing a buddy if and only if there is an existing buddy 
connection between the two buddies.
'''
@bp.route('/removebuddy', methods=['GET', 'POST'])
@login_required
def removeBuddy():
    form = RemoveBuddyForm()
    # read id from query string
    br_id = int(request.args.get("id"))
    br = BuddyRelation.query.filter_by(id=br_id).first()
    user = User.query.filter_by(username=current_user.username).first()
    # if the user does not have a buddy relation, redirect the user to the dashboard.
    if br is None:
        return redirect(url_for('dashboard.dashboard'))
    if user:
        # if the query result does not match the user id, redirect the user to the dashboard.
        if user.id != br.buddy_sender and user.id != br.buddy_receiver:
            return redirect(url_for('dashboard.dashboard'))
        else:
            if form.validate_on_submit():
                if form.data['remove_but']:
                    # remove buddy
                    si = StudyInterest.query.filter_by(id=br.study_interest_id).first()
                    course_id = si.course.id
                    # if the user id is equal to the buddy sender, update the buddy status for the subject to not sent 'N'
                    if user.id == br.buddy_sender:
                        si.buddy_status = 'N'
                        si = StudyInterest.query.filter_by(user_id = br.buddy_receiver).filter_by(course_id = course_id).first()
                        si.buddy_status = 'N'
                    # if the user id is equal to the buddy receiver, update the buddy status for the subject to not sent 'N'.
                    elif user.id == br.buddy_receiver:
                        si.buddy_status = 'N'
                        si = StudyInterest.query.filter_by(user_id = br.buddy_sender).filter_by(course_id = course_id).first()
                        si.buddy_status = 'N'

                    # delete the entry from the database and commit the changes.
                    db.session.query(BuddyRelation).filter(BuddyRelation.id == br_id).delete()
                    db.session.commit()

                    return redirect(url_for('dashboard.dashboard'))
                
                # if the user does not want to remove a buddy, redirect the user to the dashboard.
                elif form.data['dont_remove_but']:
                    # dont remove buddy, redirect to dashboard
                    return redirect(url_for('dashboard.dashboard'))
    else:
        print("********")
        print(current_user.username)


    

    return render_template('removebuddy.html', br=br, form=form)