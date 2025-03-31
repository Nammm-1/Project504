from datetime import datetime
import pyotp
import qrcode
import base64
from io import BytesIO
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'user'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_reset_required = db.Column(db.Boolean, default=False)
    
    # 2FA fields
    otp_secret = db.Column(db.String(32), nullable=True)
    otp_enabled = db.Column(db.Boolean, default=False)
    otp_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    client_info = db.relationship('Client', backref='user', uselist=False, cascade='all, delete-orphan')
    volunteer_info = db.relationship('Volunteer', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_admin(self):
        return self.role == 'admin'
        
    def is_staff(self):
        return self.role == 'staff'
        
    def is_volunteer(self):
        return self.role == 'volunteer'
        
    def is_client(self):
        return self.role == 'client'
        
    def __repr__(self):
        return f'<User {self.username}>'
        
    # 2FA Methods
    def get_totp_uri(self):
        """Get the TOTP URI for authenticator app"""
        if not self.otp_secret:
            return None
        
        app_name = "FoodPantryApp"
        totp = pyotp.TOTP(self.otp_secret)
        return totp.provisioning_uri(name=self.email, issuer_name=app_name)
    
    def get_qr_code(self):
        """Generate a QR code for the TOTP URI"""
        if not self.otp_secret:
            return None
        
        uri = self.get_totp_uri()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        buffered.seek(0)  # Reset buffer position
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"<img src='data:image/png;base64,{img_str}' alt='QR Code' class='img-fluid'>"
    
    def generate_otp_secret(self):
        """Generate a new OTP secret key"""
        self.otp_secret = pyotp.random_base32()
        self.otp_enabled = False
        self.otp_verified = False
        return self.otp_secret
    
    def verify_totp(self, token):
        """Verify a TOTP token"""
        if not self.otp_secret:
            return False
        
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(token)

class FoodItem(db.Model):
    __tablename__ = 'food_item'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20), default='item')
    expiration_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with requests (many-to-many)
    requests = db.relationship('RequestItem', back_populates='food_item', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FoodItem {self.name} ({self.quantity} {self.unit})>'

class Client(db.Model):
    __tablename__ = 'client'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(200))
    family_size = db.Column(db.Integer, default=1)
    dietary_restrictions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requests = db.relationship('ClientRequest', backref='client', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.user.full_name if self.user else "Unknown"}>'

class ClientRequest(db.Model):
    __tablename__ = 'client_request'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    pickup_date = db.Column(db.Date, nullable=True)
    special_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('RequestItem', back_populates='request', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ClientRequest #{self.id} - {self.status}>'

class RequestItem(db.Model):
    __tablename__ = 'request_item'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('client_request.id'), nullable=False)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
    quantity_requested = db.Column(db.Integer, default=1)
    quantity_fulfilled = db.Column(db.Integer, default=0)
    
    # Relationships
    request = db.relationship('ClientRequest', back_populates='items')
    food_item = db.relationship('FoodItem', back_populates='requests')
    
    def __repr__(self):
        return f'<RequestItem {self.food_item.name if self.food_item else "Unknown"} ({self.quantity_requested})>'

class Volunteer(db.Model):
    __tablename__ = 'volunteer'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skills = db.Column(db.Text, nullable=True)
    availability = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedule_entries = db.relationship('ScheduleEntry', backref='volunteer', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Volunteer {self.user.full_name if self.user else "Unknown"}>'

class ScheduleEntry(db.Model):
    __tablename__ = 'schedule_entry'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    task = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScheduleEntry {self.date} {self.start_time}-{self.end_time}>'
