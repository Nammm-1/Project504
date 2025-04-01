from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='teststaff').first()
    if user:
        print(f"Found user: {user.username}")
        
        # Reset 2FA status
        user.otp_secret = None
        user.otp_enabled = False
        user.otp_verified = False
        
        db.session.commit()
        print("Updated user 2FA settings")
        
    else:
        print("User not found")
