import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create Flask application
app = Flask(__name__)

# Load configuration
app.config.from_pyfile('config.py')
app.secret_key = os.environ.get("SESSION_SECRET", app.config['SECRET_KEY'])

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = app.config['DATABASE_URL']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

# Import models and create database tables
with app.app_context():
    # Import models (must be after db initialization)
    from models import User, FoodItem, Client, ClientRequest, Volunteer, ScheduleEntry
    db.create_all()

# Import and register routes
from routes import register_routes
register_routes(app)
