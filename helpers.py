from functools import wraps
from flask import flash, redirect, url_for, session
from flask_login import current_user, login_required
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
        print(f"Staff check: authenticated={current_user.is_authenticated}, is_staff={current_user.is_staff() if current_user.is_authenticated else False}, is_admin={current_user.is_admin() if current_user.is_authenticated else False}, username={current_user.username if current_user.is_authenticated else 'anonymous'}, role={current_user.role if current_user.is_authenticated else 'none'}")
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
    from cache import get_cached_data, set_cached_data
    
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
    
    # Try to get from cache (calendar data doesn't change for same month)
    cache_key = f"calendar_{year}_{month}"
    cached_result = get_cached_data(cache_key)
    if cached_result is not None:
        return cached_result
        
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    result = {
        'month': month,
        'year': year,
        'month_name': month_name,
        'calendar': cal,
        'prev_month': (month - 1) if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': (month + 1) if month < 12 else 1,
        'next_year': year if month < 12 else year + 1
    }
    
    # Cache for a day since calendar data is static
    return set_cached_data(cache_key, result, timeout=86400)

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
    from cache import get_cached_data, set_cached_data
    
    # Try to get from cache first (5 minute cache)
    cache_key = f"expiring_items_{days}"
    cached_result = get_cached_data(cache_key)
    if cached_result is not None:
        return cached_result
    
    today = date.today()
    expiry_cutoff = today + timedelta(days=days)
    
    result = FoodItem.query.filter(
        FoodItem.expiration_date.isnot(None),
        FoodItem.expiration_date <= expiry_cutoff,
        FoodItem.expiration_date >= today,
        FoodItem.quantity > 0
    ).order_by(FoodItem.expiration_date).all()
    
    # Cache for 5 minutes
    return set_cached_data(cache_key, result, timeout=300)

def get_low_stock_items(threshold=10):
    """Get items with stock below the specified threshold"""
    from models import FoodItem
    from cache import get_cached_data, set_cached_data
    
    # Try to get from cache first (5 minute cache)
    cache_key = f"low_stock_items_{threshold}"
    cached_result = get_cached_data(cache_key)
    if cached_result is not None:
        return cached_result
    
    result = FoodItem.query.filter(
        FoodItem.quantity <= threshold, 
        FoodItem.quantity > 0
    ).order_by(FoodItem.quantity).all()
    
    # Cache for 5 minutes
    return set_cached_data(cache_key, result, timeout=300)

def require_2fa(f):
    """
    Decorator to ensure 2FA verification is completed when required
    This decorator should be applied after login_required
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If user has 2FA enabled but not verified in current session
        if current_user.is_authenticated and current_user.otp_enabled and 'otp_verified' not in session:
            # Store the current path for later redirection
            session['next'] = url_for(f.__name__, **kwargs)
            flash('Please verify your identity with two-factor authentication.', 'warning')
            return redirect(url_for('two_factor_verify'))
        return f(*args, **kwargs)
    return decorated_function
