from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os


UPLOAD_FOLDER = '/Users/masoud/projects/EnterpriseWiki/setup/static/uploaded_pics'

enterprise_wiki = Flask(__name__, template_folder='/Users/masoud/projects/EnterpriseWiki/templates')
enterprise_wiki.config['SESSION_TYPE'] = 'filesystem'
enterprise_wiki.secret_key = '410ecd8b628fad11e0c7fb742361aa30'
enterprise_wiki.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/masoud/projects/EnterpriseWiki/armaghan.db'
enterprise_wiki.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy modification tracking
enterprise_wiki.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploaded_pics')


db = SQLAlchemy(enterprise_wiki)
bcrypt = Bcrypt(enterprise_wiki)
login_manager = LoginManager(enterprise_wiki)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from setup import db, enterprise_wiki
from setup.models import Users, Post, Img
import setup.routes

with enterprise_wiki.app_context():
    db.create_all()
    Users.query.all()
    Post.query.all()
    Img.query.all()

