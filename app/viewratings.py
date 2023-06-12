# Author: Aaron Alakkadan
from flask import Blueprint, render_template, url_for, redirect, request, session 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.dashboard import *
from app.models.user import User
from app.models.buddyrating import BuddyRating
from sqlalchemy import desc

'''
The is the form class for the view ratings form
'''
class viewRatingsForm(FlaskForm):
    view_rating_but = SubmitField("Button")

'''
The view ratings function enscapulates all business rules for displaying a user's buddy rating

Query the database based on the current user then you query the database based on the rating receiver
because the buddy receiver would like to view the rating that the buddy sender has given them.
'''
bp = Blueprint('viewratings', __name__, url_prefix='/')
@bp.route('/viewratings', methods=['GET', 'POST'])
@login_required
def viewRatings():
    form = viewRatingsForm()
    user = User.query.filter_by(username=current_user.username).first()
    buddy_rating = BuddyRating.query.filter_by(rating_receiver=user.id).order_by(desc(BuddyRating.rating_date)).all()
    return render_template('viewratings.html', form=form, buddy_rating=buddy_rating)