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
    
    # Check if admin users exist, create one if not
    admin_count = User.query.filter_by(role='admin').count()
    
    # Get the default admin password from environment or use a default
    default_admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "password123")
    
    app.logger.info(f"Checking for admin users. Count: {admin_count}")
        
    if admin_count == 0:
        try:
            # Create default admin user
            admin = User(
                username='admin',
                email='admin@foodpantry.org',
                role='admin',
                full_name='System Administrator',
                password_reset_required=True
            )
            admin.set_password(default_admin_password)
            db.session.add(admin)
            db.session.commit()
            
            app.logger.info("Default admin user created successfully.")
            print(f"Default admin user created with username: 'admin' and password: '{default_admin_password}'")
            print("Please change this password immediately after logging in.")
        except Exception as e:
            app.logger.error(f"Error creating admin user: {str(e)}")
            print(f"Error creating admin user: {str(e)}")

# Import and register routes
from routes import register_routes
register_routes(app)
