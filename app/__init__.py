# Author: Aaron Alakkadan, Talal Hakki, Matt Faiola 
import os 
from flask import Flask
from app.extensions import db, bcrypt, login_manager, email
from flask_bcrypt import Bcrypt
from flask_mail import Mail


'''
The function create_app is a factory funnction which creates a flask app
It is called fron flask run command when you execute in terminal 
'''
def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.from_object("instance.config.TestConfig")
    else: 
        app.config.from_object("instance.config.Config")

    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024     # 5MB

    with app.app_context():
        db.init_app(app)
        login_manager.login_view = "login"
        login_manager.init_app(app)
        bcrypt = Bcrypt(app)
        email = Mail(app)
        
    
    # Initialize all the blueprints using the app instance and the register blueprint method 
    # Inline import is required here to avoid circular dependency 
    from . import auth, dashboard, findstudybuddy, subjectselection, materialsupload, materialsview, rate, viewratings, profile, removebuddy
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(findstudybuddy.bp)
    app.register_blueprint(subjectselection.bp)
    app.register_blueprint(materialsupload.bp)
    app.register_blueprint(materialsview.bp)
    app.register_blueprint(rate.bp)
    app.register_blueprint(viewratings.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(removebuddy.bp)

    
    return app

