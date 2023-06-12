# Author: Aaron Alakkadan, Matt Faiola 
from app.models import *
from app.models.user import User
from app.models.studyinterest import StudyInterest
from app.models.buddyrelation import BuddyRelation
from app.models.document import Document
from app.models.buddyrating import BuddyRating
from app.models.course import Course, Subject
from app.extensions import db
import os
import csv
import random
from statistics import mean

'''
The function import_courses functionality is to import the sortedCours csv file into the database.
'''
def import_courses(file_path):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            model_instance = Course(subject_code=row[0], course_number=row[1], course_name=row[2])
            db.session.add(model_instance)
        db.session.commit()

'''
The function import_subject_code functionality is to import the sortedCode csv file into the database.
'''
def import_subject_code(file_path):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for row in csv_reader:
            model_instance = Subject(subject_code=row[0], subject_name=row[1])
            db.session.add(model_instance)
        db.session.commit()

'''
The function create_db functionality is to create the database locally.
If the database already exists, it will delete the database and create a new one.
'''
def create_db():
    from app import create_app

    if os.path.isfile('instance/database.db'):
        os.remove('instance/database.db')
        with create_app().app_context():
            db.create_all()
            print("Loading csv files")
            import_subject_code('instance/sortedCode.csv')
            import_courses('instance/sortedCourse.csv')
        print("New Database Created")
    else:
        print("The file does not exist")
        with create_app().app_context():
            db.create_all()
        print("Database Created")


'''
The function seed_data functionality is to provide sample data locally therefore when
recreating the database locally you can call this function and it will store this data locally.
'''
def seed_data():
   from app.extensions import db, bcrypt
   from app import create_app

   with create_app().app_context():
        hashed_password = bcrypt.generate_password_hash("123456")
        new_user = User(first_name="Aaron", last_name="Alakkadan",  
                            username="aalakkad@syr.edu", password=hashed_password,
                            token="1234", is_verified=True, phone_number="3155777555", about_me="I am a student at Syracuse University")
        new_user2 = User(first_name="Matt", last_name="Faiola",  
                            username="mjfaiola@syr.edu", password=hashed_password,
                            token="234234", is_verified=True, phone_number="3155555555", about_me="I am a student at Syracuse University")
        new_user3 = User(first_name="Talal", last_name="Hakki",  
                            username="thakki@syr.edu", password=hashed_password,
                            token="4567", is_verified=True, phone_number="3151231234", about_me="I am a student at Syracuse University")
        new_user4 = User(first_name="John", last_name="Fuhrman",  
                            username="jnfuhrma@syr.edu", password=hashed_password,
                            token="23498", is_verified=True, phone_number="31519463274", about_me="I am a student at Syracuse University")
        new_user5 = User(first_name="Alec", last_name="Marcus",  
                            username="almarcus@syr.edu", password=hashed_password,
                            token="45456", is_verified=True, phone_number="3151633434", about_me="I am a student at Syracuse University")
        db.session.add(new_user)
        db.session.add(new_user2)
        db.session.add(new_user3)
        db.session.add(new_user4)
        db.session.add(new_user5)
        db.session.commit()
        # adds 5 study interests for each user
        # with random profiency scores
        users = [new_user, new_user2, new_user3, new_user4, new_user5]
        courses = [44, 500, 411, 28, 3400]
        for user in users:
            for i in range(0, 5):
                si = StudyInterest()
                si.user_id = user.id
                si.course_id = courses[i]
                pro_ans1 = random.randint(1, 5)
                si.pro_ans1 = pro_ans1
                pro_ans2 = random.randint(1, 5)
                si.pro_ans2 = pro_ans2
                pro_ans3 = random.randint(1, 5)
                si.pro_ans1 = pro_ans3
                si.pro_score = round(mean([int(pro_ans1), int(pro_ans2), int(pro_ans3)]),2)
                #si.buddy_status = 'S'
                db.session.add(si)
        db.session.commit()

        #adds pending 5 invitations from aaron to matt
        
        # for x in range(1, 5):
        #     br = BuddyRelation()
        #     br.buddy_sender = new_user.id
        #     br.buddy_receiver = new_user2.id
        #     br.study_interest_id = x
        #     br.invitation_status = 'S'
        #     db.session.add(br)
        # db.session.commit()

'''
The function seed_test_data functionality is to provide sample data locally therefore when
recreating the database locally you can call this function and it will store this data locally.
'''
def seed_test_data():
    from app.extensions import db, bcrypt
    from app import create_app

    with create_app().app_context():
        hashed_password = bcrypt.generate_password_hash("123456")
        if not User.query.filter_by(username="test1@syr.edu").count():
            test_user = User(first_name="test1", last_name="user1",  
                            username="test1@syr.edu", password=hashed_password,
                            token="9001", is_verified=True, phone_number="9001231234", about_me="I am a student at Syracuse University")
            db.session.add(test_user)
            db.session.commit()

        if not User.query.filter_by(username="tsender@syr.edu").count():
            test_sender = User(first_name="testsender", last_name="user2",  
                            username="tsender@syr.edu", password=hashed_password,
                            token="9002", is_verified=True, phone_number="9001231235", about_me="I am a student at Syracuse University")
            db.session.add(test_sender)
            db.session.commit()

        if not User.query.filter_by(username="tsender@syr.edu").count():   
            test_receiver = User(first_name="testreceiver", last_name="user3",  
                            username="treceiver@syr.edu", password=hashed_password,
                            token="9003", is_verified=True, phone_number="9001231236", about_me="I am a student at Syracuse University")
            db.session.add(test_receiver)
            db.session.commit()
     