# Author: Aaron Alakkadan, Talal Hakki, Matt Faiola 
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, session, current_app, Flask, send_file
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from app.auth import *
from app.dashboard import *
from app.models.document import *
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
from datetime import datetime

'''
This is the form class for materials upload 
'''
class materialsUploadForm(FlaskForm):
    material_but = SubmitField("Upload")
    comment = StringField(validators=[Length(min=0, max=50)], render_kw={"placeholder": "Add a comment", "value": ""})


# This function allows a user to share a document and a comment with a Buddy.
bp = Blueprint('materialsupload', __name__, url_prefix='/')
@bp.route('/materialsupload', methods=['GET','POST'])
@login_required
def materialsUpload():
    form = materialsUploadForm()
    br_id = int(request.args.get("id"))
    br = BuddyRelation.query.filter_by(id=br_id).first()
    # if the user does not have a buddy, redirect the user to the dashboard.
    if br is None:
        return redirect(url_for('dashboard.dashboard'))
    user = User.query.filter_by(username=current_user.username).first()
    buddy = br.get_buddy(current_user.username)
    msg = ''
    upload_message = ''
    file_name = ""
    # if the user is eligible to upload a document, allow for document sharing. The user must have less than 20
    # daily files shared to be able to share a file.
    if br.can_user_upload(current_user.username):
        if form.data['material_but']:
            try:
                
                file = request.files['file']
                
                if not os.path.exists('app/uploads'):
                    os.makedirs('app/uploads')
                
                # if the user has selected a document to upload and the file size is less than or equal to 5MB,
                # add a new entry to the Document database table with the user's id, Buddy receiver's id,
                # selected subject title, comment, and file content.
                if file:

                    # if the selected document has a file size of more than 5MB, display an error message to the
                    # user stating that uploaded files must be less than the 5MB limit.
                    if file.content_length > 1024 * 5:
                        print("max file size")
                        msg = 'File is larger than the 5MB limit.'
                        return render_template('materialsupload.html', form=form, br=br, buddy=buddy, msg=msg, file_name=file_name, upload_message=upload_message)
                        
                    blob_data = None
                    file.save(os.path.join('app/uploads/', secure_filename(file.filename)))
                    with open(os.path.join('app/uploads/', secure_filename(file.filename)), "rb") as f:
                        blob_data = bytearray(f.read())
                    d = Document(buddy_sender=user.id, buddy_receiver=buddy.id,
                                course_id=br.study_interest.course.id, comment=form.comment.data, name=file.filename, content=blob_data)
                    db.session.add(d)
                    db.session.commit()

                    file_name = file.filename
                    
                    # display upload success message to the user
                    msg = 'File uploaded successfully!'

                    # ensuring that the upload counter is a valid positive number.
                    if current_user.username == br.sender.username:
                        br.upload_count_sender += 1
                        if br.upload_count_sender < 0:
                            msg = 'ERROR Upload count is negative.'
                    elif current_user.username == br.receiver.username:
                        br.upload_count_receiver += 1
                        if br.upload_count_sender < 0:
                            msg = 'ERROR Upload count is negative.'
                    # ensuring that the Buddy receiver is a Buddy of the current user.
                    else:
                        msg = 'ERROR User not in buddy relation.'

                    db.session.commit()
                # display a message if the user does not select a file to upload.
                else:
                    msg = 'No file selected.'
            # exception thrown if the file size is greater than 5MB.        
            except RequestEntityTooLarge:
                msg = 'File is larger than the 5MB limit.'
                

    if not br.can_user_upload(current_user.username):
        upload_message = 'You have reached the maximum number of uploads for today.'

    return render_template('materialsupload.html', form=form, br=br, buddy=buddy, msg=msg, file_name=file_name, upload_message=upload_message)


