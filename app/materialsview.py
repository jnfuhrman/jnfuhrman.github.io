# Author: Aaron Alakkadan, Matt Faiola, Talal Hakki 
from flask import Blueprint, render_template, url_for, redirect, request, session , send_file
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.dashboard import *
from app.models.document import *
from wtforms.fields import StringField, SelectField, RadioField
from io import BytesIO
from sqlalchemy.orm import joinedload
from sqlalchemy import exists


'''
This is the form class for materials view 
'''
class materialsViewForm(FlaskForm):
    course_name = SelectField('Course Name', validators=[InputRequired()], choices=[])
    material_view_but = SubmitField("View")


# This function allows a user to view and download documents shared by Buddies.
bp = Blueprint('materialsview', __name__, url_prefix='/')
@bp.route('/materialsview', methods=['GET', 'POST'])
@login_required
def materialsView():
    form = materialsViewForm()
    user = User.query.filter_by(username=current_user.username).first()
    
    #COMMENTED CODE FIXES DEPRICATION WARNING IN TEST CASE BUT IS NOT TESTED FUNCTINONALLY
    docs_qry = db.session.query(Document.course_id).filter(Document.buddy_receiver == user.id).distinct(Document.course_id)
    #docs_subquery = db.session.query(Document.course_id).distinct().filter_by(buddy_receiver=user.id).subquery()
    list_of_doc = []
    courses = db.session.query(Course).filter(Course.id.in_(docs_qry)).all()
    #courses = db.session.query(Course).filter(exists().where(Course.id == docs_subquery.c.course_id)).all()

    #print("The courses are : ", courses)
    #print(courses.statement)
    form.course_name.choices = [("", "")] + [(c.id, c.course_name) for c in courses]
    if form.validate_on_submit:
        if form.data['material_view_but']:         
            list_of_doc = Document.query.filter_by(buddy_receiver=user.id, course_id=form.course_name.data).all()
    return render_template('materialsview.html', form=form, list_of_doc=list_of_doc)


# This function query's the database for the user and the associated incoming document.
@bp.route('/docView', methods=['GET'])
@login_required
def docView():
    doc_id = request.args.get("id")
    user = User.query.filter_by(username=current_user.username).first()
    doc = Document.query.filter_by(id=doc_id).first()
    return send_file(BytesIO(doc.content), as_attachment=True, download_name=doc.name)