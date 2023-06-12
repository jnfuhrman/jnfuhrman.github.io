#Author: Aaron Alakkadan
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

'''
Motivation: extension is brought in to avoid circular dependency.

One way to initiate globally used objects like SQLAlchemy is to put them in create app.

If you choose this way then it created circular dependency for other modules.

Extension design allows create_app to refer extensions and other modules like auth.py to refer to extensions
Every module will get the same instance of these objects.  
'''
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
email = Mail()

