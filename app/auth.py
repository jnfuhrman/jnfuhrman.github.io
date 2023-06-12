# Author: Aaron Alakkadan, Matt Faiola, Talal Hakki
from flask import Blueprint, render_template, url_for, redirect, request, session, current_app
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, validators
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt
from app.models.user import User
from app.extensions import db, bcrypt, login_manager, email
from flask_mail import Message
import random  

'''
send email subject lines
'''
subjectEmailConfirmation = "Email Confirmation"
subjectPasswordReset = "Password Reset"

bp = Blueprint('auth', __name__, url_prefix='/')

'''
This function loads user from the database
'''
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))

'''
This is a form class for the registration 
'''
class RegisterForm(FlaskForm):
    first_name = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "First Name"})
    
    last_name = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Last Name"})
                             
    username = StringField(validators=[InputRequired(), Email(granular_message="invalid email address"), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
            min=4, max=20)], render_kw={"placeholder": "Password"})
    
    re_enter_password = PasswordField('Re-enter Password',[validators.DataRequired(),validators.Length(
        min=4, max=20)], render_kw={"placeholder": "Re-enter New Password"})

    submit = SubmitField("SignUp")

    '''
    This function validates that the username is an valid @syr.edu email and checks that
    an existing user cannot sign up again with an existing username 
    '''
    def validate_username(self, username):
        if not username.data.endswith("@syr.edu"):
            raise ValidationError("Your email address must be a valid Syracuse University email")
        existing_user_username = User.query.filter_by(
            username=username.data).first()

        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one.")

'''
This is the form class for login 
'''
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login") 


'''
This is the form class for forgot password  
'''
class ForgotForm(FlaskForm):
     username = StringField(validators=[InputRequired(), Email(granular_message="invalid email address"), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
     submit = SubmitField("Submit")

'''
This is the form class for password reset 
'''
class PasswordResetForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Email(granular_message="invalid email address"), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('New Password',[validators.DataRequired(),validators.Length(
        min=4, max=20)], render_kw={"placeholder": "New Password"})
    re_enter_password = PasswordField('Re-enter Password',[validators.DataRequired(),validators.Length(
        min=4, max=20)], render_kw={"placeholder": "Re-enter New Password"})
    submit = SubmitField("Submit")

'''
This is the form class for Email Confirmation
'''
class EmailConfirmation(FlaskForm):
    msg = "Please check your email to confirm validity"  

'''
This is the form class for Forgot Password Confirmation 
'''
class ForgotConfirmation(FlaskForm):
    msg = "Please check your email for a link to reset password"

'''
The reset_password function encapulates all the business rules needed when the user is resetting their password.
The first rule is to check if the user exists. If the user doesn't exist it will throw an error.

The second rule is to also check if the password is the same as the re_enter_password. It is does not match it will throw
an error. 

The third rule is to check if the token exists if the token does exist that means that the user did
not click the link in the email and it will throw an error.

Then it will check if the validity of the token if the token is invalid it will throw an error. 
If the user's token in the database matches the token then change the old password to the new password entered and store it in the database. 
'''
@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    msg = ""
    form = PasswordResetForm()
    token = request.args.get("t") # gets the value of the token in the args dictionary 
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if form.password.data == form.re_enter_password.data:
                if token:
                    if user.token == token:
                        hash_pass = bcrypt.generate_password_hash(form.password.data)
                        user.password=hash_pass
                        db.session.add(user)
                        db.session.commit()
                        msg = "Success, passwords match."
                        return redirect(url_for('auth.login'))
                    
                    else:
                        msg = "Invalid token"
                else:
                    msg = "Empty token"
            
            else:
                msg = "Passwords do not match, try again."
                
        else:
            msg = "Invalid User"
    return render_template('reset_password.html', form=form, msg=msg)
            

'''
The signup function encapsulates all the business rules for signing up the new user.

Once the business rules have passed the user will receive an confirmation email this to the eliminate any phantom signup.

Once user signs up, the user will be redirected to the email confirmation page which will remind the user to check 
their email in order to verify it.
'''
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    msg = ""
    if form.validate_on_submit():
        if form.password.data == form.re_enter_password.data:
            token =  random.randint(10**9,10**10)
            html_msg = email_content_email_confirmation(
                username=form.username.data, 
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email_confirmation_url=url_for('auth.login', _external=True),
                token=token 
                )
            send_email(email_address=form.username.data, msg_html=html_msg, subject=subjectEmailConfirmation)
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(first_name=form.first_name.data, last_name=form.last_name.data,  
                            username=form.username.data, password=hashed_password,
                            token=token)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.emailconfirmation'))
        else:
            msg = "Passwords do not match, try again."
    return render_template('register.html', form=form, msg=msg)


'''
The emailconfirmation function renders the emailconfirmation page which tells the user to check their email
to verify them.
'''
@bp.route('/emailconfirmation', methods=['GET'])
def emailconfirmation():
    form = EmailConfirmation()
    return render_template('emailconfirmation.html', form=form, msg=form.msg)

'''
The login function encapulates all the business rules for logging into the system.

The login function checks if the user's username exists after query the database. If it does not exist it will
throw an error. If it does exist it will check the hashed password of the user. 

When a user login for the first time, the user must click the link in the email that contains token.
If token is not existing the system will throw an error.
If the token does exist that means that the user did not click the link in the email and it will throw an error.

If the user's token in the database matches the token then the system marks the user as verified.
Subsequent login does not require token, it only requires username and password.    
'''
@bp.route('/login', methods=['GET','POST'])
def login():
    msg = ""
    form = LoginForm()
    token = request.args.get("t") # gets the value of the token in the args dictionary 
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                if token:
                    if user.token == token:
                        user.is_verified = True
                        db.session.add(user)
                        db.session.commit()
                    else:
                        msg = "Invalid token"
                        return render_template('login.html', form=form, msg=msg)
                    
                else:
                    if not user.is_verified:
                        msg = "Did not click on the link which was sent to your email"
                        return render_template('login.html', form=form, msg=msg)
                    
                login_user(user)
                return redirect(url_for('dashboard.dashboard'))
            else:
                msg = "Invalid Login"
        else:
            msg = "Invalid Login" 
    return render_template('login.html', form=form, msg=msg)


'''
This is a form class for contactUs
'''
class contactUs(FlaskForm):
    contactButton = SubmitField("Contact Us")

'''
The home function encapulates the contact us feature.
It captures information from the user on the landing page and sends an email to the admin 
'''
@bp.route('/', methods=['GET', 'POST'])
def home():
    form = contactUs()
    if form.validate_on_submit():
        if form.data['contactButton']:
            return redirect(url_for('auth.home'))
    
    if request.method == 'POST':
        name = request.form['name']
        email_address = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        our_email = "su.study.buddy@gmail.com"
        msg = Message(subject=subject, sender='su.study.buddy@gmail.com', recipients=[our_email])
        msg.body = f"Name: {name}\nEmail: {email_address}\n\n{message}"
        email.send(msg)

        return render_template('home.html', form=form)

    return render_template('home.html', form=form)


'''
The logout function checks that you must be logged in in order for the user to logout which will
redirect them to the logout page 
'''
@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

'''
The forgot function encapsulates the business rules for forgot password feature
A user must be a verified user before they can use this feature.

Once the user enters their username in the forgot password page, the system sends an email. 
It will redirect the user to the forgot confirmation page where it will remind them to check their email.  
'''
@bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm() 
    msg = ""
    if form.validate_on_submit():
        token = random.randint(10**9,10**10)
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.is_verified:
                user.token = token
                db.session.add(user)
                db.session.commit()

                html_msg = email_content_password_reset(
                    username=form.username.data,
                    first_name = user.first_name,
                    last_name = user.last_name,
                    reset_password_url=url_for('auth.reset_password', _external=True),
                    token=token)
        
                send_email(email_address=form.username.data, msg_html=html_msg, subject=subjectPasswordReset)
        
                return redirect(url_for('auth.forgotconfirmation'))
            
            else:
                msg = "Your email is not verified"
        else:
            msg = "Your email is not registered"
        
    return render_template('forgot.html', form=form, msg=msg)

'''
The forgot confirmation function renders the forgot confirmation template which is a page that tells
the user to go to check their email for the password reset 
'''
@bp.route('/forgotconfirmation', methods=['GET'])
def forgotconfirmation():
    form = ForgotConfirmation()
    return render_template('forgotconfirmation.html', form=form, msg=form.msg)

'''
The send email function is a generic function that sends the email from the admin's official email which is su.study.buddy@gmail.com
to the email of the user.
'''
def send_email(email_address, msg_html, subject):
    sendSubject = subject
    msg = Message(
                subject = sendSubject,
                sender ='su.study.buddy@gmail.com',
                recipients = [email_address]
               )

    with current_app.open_resource("static/images/logo-study-buddy.png", 'rb') as lock:
        msg.attach('logo-study-buddy.png', 'image/png', lock.read(), 'inline', headers=[['Content-ID','<lock>']])

    msg.html = msg_html 
    email.send(msg)
    return msg

'''
The email_content_password_reset function generates the email password reset content to the user
and generates the url
'''
def email_content_password_reset(username, first_name, last_name, reset_password_url, token):
    url = f"{reset_password_url}?t={token}"
    return render_template('reset_pw_email.html', username=username, first_name=first_name, last_name=last_name, url=url)

'''
The email_content_email_confirmation function generates the email confirmation content to the user for signup
and generates the url
'''
def email_content_email_confirmation(username, first_name ,last_name, email_confirmation_url, token):
    url = f"{email_confirmation_url}?t={token}"
    return render_template('email.html', username=username, first_name=first_name, last_name=last_name, url=url)
