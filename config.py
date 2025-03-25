import os

# SQLite Database configuration
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'food_pantry.db')
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{SQLITE_DB_PATH}")

# Application configuration
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-replace-in-production")
DEBUG = True

# Define roles
ROLES = {
    'ADMIN': 'admin',
    'STAFF': 'staff',
    'VOLUNTEER': 'volunteer',
    'CLIENT': 'client'
}

# Food categories
FOOD_CATEGORIES = [
    'Canned Goods',
    'Dry Goods',
    'Frozen Foods',
    'Fresh Produce',
    'Dairy',
    'Meat',
    'Bakery',
    'Beverages',
    'Personal Care',
    'Other'
]

# Request status options
REQUEST_STATUS = [
    'Pending',
    'Approved',
    'In Progress',
    'Completed',
    'Cancelled'
]

# Time slots for volunteer schedules (30 min increments)
TIME_SLOTS = [
    '09:00 AM', '09:30 AM', 
    '10:00 AM', '10:30 AM', 
    '11:00 AM', '11:30 AM',
    '12:00 PM', '12:30 PM',
    '01:00 PM', '01:30 PM',
    '02:00 PM', '02:30 PM',
    '03:00 PM', '03:30 PM',
    '04:00 PM', '04:30 PM',
    '05:00 PM'
]
