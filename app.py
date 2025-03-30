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
    
    with open('/home/runner/workspace/logs.txt', 'a') as f:
        f.write(f"Checking admin users. Count: {admin_count}\n")
        
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
            admin.set_password('adminpassword')
            db.session.add(admin)
            db.session.commit()
            
            with open('/home/runner/workspace/logs.txt', 'a') as f:
                f.write("Default admin user created successfully.\n")
                
            print("Default admin user created.")
        except Exception as e:
            with open('/home/runner/workspace/logs.txt', 'a') as f:
                f.write(f"Error creating admin user: {str(e)}\n")
            print(f"Error creating admin user: {str(e)}")

# Import and register routes
from routes import register_routes
register_routes(app)
