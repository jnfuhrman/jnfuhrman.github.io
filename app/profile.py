# Author: Aaron Alakkadan, Talal Hakki
from flask import Blueprint, render_template, url_for, redirect, request, session 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.dashboard import *
import flask_login

'''
This is the form class for profile.
'''
class profileForm(FlaskForm):
    homeButton = SubmitField("Home")
    logoutButton = SubmitField("Logout")
    saveButton = SubmitField("Save")
    phoneNumber = StringField(validators=[Length(
        min=0, max=15)],render_kw={"placeholder": "Phone Number"})
    aboutMe = StringField(validators=[Length(
        min=0, max=50)], render_kw={"placeholder": "About Me"})

bp = Blueprint('profile', __name__, url_prefix='/')
'''
The profile function encapsulates all business rules for creating a profile.
The phone number and about me are optional fields that the user is not required to fill in.
The profile information of other users will be displayed when searching for a buddy.
'''
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = profileForm()
    msg = ""
    user = User.query.filter_by(username=current_user.username).first()
    if user:      
        if request.method == 'GET':
            form.phoneNumber.data = user.phone_number
            form.aboutMe.data = user.about_me
        
        if form.data['saveButton']:
            # phoneNumber and aboutMe are optional fields
           
            # if phone number is too long or is invalid, send message to user
            if len(form.phoneNumber.data) > 15:
                msg = "Invalid phone number must be less than 15 characters"
                return render_template('profile.html', form=form, msg=msg)
            
            # if phone number is not alphanumeric or is invalid, send message to user
            if form.phoneNumber.data and not form.phoneNumber.data.isnumeric():
                msg = "Invalid phone number, please use digits"
                return render_template('profile.html', form=form, msg=msg)
            
            # if the length of about me is larger than 50, send message to the user 
            if len(form.aboutMe.data) >= 50:
                msg = "Invalid, the maximum character limit for about me description is 50"
                return render_template('profile.html', form=form, msg=msg)
                        
            
            user.phone_number = form.phoneNumber.data
            user.about_me = form.aboutMe.data
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('profile.profile'))
                     
        # if the home button is clicked, redirect the user to the dashboard.
        elif form.data['homeButton']:
            return redirect(url_for('dashboard.dashboard'))

        # if the logout button is clicked, redirect the user to the login page.
        elif form.data['logoutButton']:
            return redirect(url_for('auth.login'))

    return render_template('profile.html', form=form, msg=msg)
