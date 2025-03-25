from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
import calendar
from datetime import datetime, timedelta, date

def role_required(*roles):
    """
    Decorator to restrict access to specific user roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
                
            if current_user.role not in roles and 'admin' not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator for admin-only access
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    """
    Decorator for staff access (includes admins)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (not current_user.is_staff() and not current_user.is_admin()):
            flash('Staff access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_upcoming_week_dates():
    """
    Get a list of dates for the upcoming week starting from today
    """
    today = date.today()
    return [today + timedelta(days=i) for i in range(7)]

def get_month_calendar(year=None, month=None):
    """
    Get calendar data for the specified month or current month
    """
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
        
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    return {
        'month': month,
        'year': year,
        'month_name': month_name,
        'calendar': cal,
        'prev_month': (month - 1) if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': (month + 1) if month < 12 else 1,
        'next_year': year if month < 12 else year + 1
    }

def format_date(date_obj):
    """Format date for display"""
    if not date_obj:
        return ''
    return date_obj.strftime('%m/%d/%Y')

def format_datetime(dt_obj):
    """Format datetime for display"""
    if not dt_obj:
        return ''
    return dt_obj.strftime('%m/%d/%Y %I:%M %p')

def get_expiring_items(days=7):
    """Get items expiring within the specified number of days"""
    from models import FoodItem
    today = date.today()
    expiry_cutoff = today + timedelta(days=days)
    
    return FoodItem.query.filter(
        FoodItem.expiration_date.isnot(None),
        FoodItem.expiration_date <= expiry_cutoff,
        FoodItem.expiration_date >= today,
        FoodItem.quantity > 0
    ).order_by(FoodItem.expiration_date).all()

def get_low_stock_items(threshold=10):
    """Get items with stock below the specified threshold"""
    from models import FoodItem
    return FoodItem.query.filter(FoodItem.quantity <= threshold, FoodItem.quantity > 0).order_by(FoodItem.quantity).all()
