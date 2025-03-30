from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_reset_required = db.Column(db.Boolean, default=False)
    
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

class FoodItem(db.Model):
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
