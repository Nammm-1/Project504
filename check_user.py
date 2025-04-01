from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='teststaff').first()
    if user:
        print(f'User exists: True')
        print(f'Username: {user.username}')
        print(f'Role: {user.role}')
        print(f'Password reset required: {user.password_reset_required}')
    else:
        print('User does not exist')
