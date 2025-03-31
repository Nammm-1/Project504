from flask import render_template, redirect, url_for, flash, request, jsonify, abort, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import calendar
from sqlalchemy import func

from app import db
from models import User, FoodItem, Client, ClientRequest, RequestItem, Volunteer, ScheduleEntry
from forms import (
    LoginForm, RegistrationForm, AdminUserCreateForm, ClientProfileForm, VolunteerProfileForm,
    FoodItemForm, ClientRequestForm, RequestItemForm, RequestUpdateForm, RequestItemUpdateForm,
    ScheduleEntryForm, SearchForm, DateRangeForm, PasswordChangeForm, TwoFactorSetupForm,
    TwoFactorVerifyForm
)
from helpers import (
    role_required, admin_required, staff_required, get_upcoming_week_dates,
    get_month_calendar, format_date, format_datetime, get_expiring_items,
    get_low_stock_items, require_2fa
)
from config import FOOD_CATEGORIES, ROLES, REQUEST_STATUS, TIME_SLOTS

def register_routes(app):
    # Authentication routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            # Check if 2FA is required but not completed
            if 'otp_verified' not in session and current_user.otp_enabled:
                return redirect(url_for('two_factor_verify'))
            return redirect(url_for('dashboard'))
            
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                # Check if password reset is required
                if user.password_reset_required:
                    # Don't log in yet, but save user ID in session to access it after password reset
                    session['password_reset_user_id'] = user.id
                    flash('You must change your password before continuing.', 'warning')
                    return redirect(url_for('user_reset_password', user_id=user.id))
                
                # Log user in
                login_user(user)
                next_page = request.args.get('next')
                
                # Check if 2FA is enabled for this user
                if user.otp_enabled:
                    # If 2FA is enabled, redirect to the 2FA verification page
                    session['next'] = next_page
                    return redirect(url_for('two_factor_verify'))
                
                # If 2FA is not set up but the system requires it for first login, set up 2FA
                if not user.otp_enabled and not user.otp_verified:
                    # Generate a new OTP secret for the user
                    user.generate_otp_secret()
                    db.session.commit()
                    flash('For security reasons, you need to set up two-factor authentication.', 'info')
                    return redirect(url_for('two_factor_setup'))
                
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')
                
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        # Clear all session data including 2FA verification status
        session.clear()
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
        
    @app.route('/2fa/setup', methods=['GET', 'POST'])
    @login_required
    def two_factor_setup():
        # Check if user already has verified 2FA
        if current_user.otp_verified and current_user.otp_enabled:
            flash('Two-factor authentication is already set up.', 'info')
            return redirect(url_for('dashboard'))
            
        # Ensure user has a secret
        if not current_user.otp_secret:
            current_user.generate_otp_secret()
            db.session.commit()
            
        # Generate QR code for the user's secret
        qr_code = current_user.get_qr_code()
        form = TwoFactorSetupForm()
        
        if form.validate_on_submit():
            if current_user.verify_totp(form.token.data):
                current_user.otp_verified = True
                current_user.otp_enabled = True
                db.session.commit()
                
                # Mark session as verified with 2FA
                session['otp_verified'] = True
                
                flash('Two-factor authentication has been successfully set up!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid verification code. Please try again.', 'danger')
                
        return render_template('auth/2fa_setup.html', form=form, qr_code=qr_code, secret=current_user.otp_secret)
        
    @app.route('/2fa/verify', methods=['GET', 'POST'])
    @login_required
    def two_factor_verify():
        # If user doesn't have 2FA enabled or session is already verified
        if not current_user.otp_enabled or 'otp_verified' in session:
            return redirect(url_for('dashboard'))
            
        form = TwoFactorVerifyForm()
        
        if form.validate_on_submit():
            if current_user.verify_totp(form.token.data):
                session['otp_verified'] = True
                
                # Get the next page from session or default to dashboard
                next_page = session.pop('next', None)
                
                flash(f'Welcome back, {current_user.username}!', 'success')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid verification code. Please try again.', 'danger')
                
        return render_template('auth/2fa_verify.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists. Please choose a different one.', 'danger')
                return render_template('register.html', form=form)
                
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('register.html', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                password_reset_required=False  # Self-registered users don't need to reset password
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            # Create client or volunteer profile based on role
            if user.role == 'client':
                client = Client(user_id=user.id)
                db.session.add(client)
                db.session.commit()
                
            elif user.role == 'volunteer':
                volunteer = Volunteer(user_id=user.id)
                db.session.add(volunteer)
                db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        return render_template('register.html', form=form)

    # Dashboard route
    @app.route('/dashboard')
    @login_required
    @require_2fa
    def dashboard():
        from cache import get_cached_data, set_cached_data
        
        # Admin/Staff dashboard
        if current_user.is_admin() or current_user.is_staff():
            # Try to get cached dashboard data
            cache_key = f"admin_dashboard_{current_user.id}"
            dashboard_data = get_cached_data(cache_key)
            
            if dashboard_data is None:
                # Get statistics for dashboard
                total_inventory = FoodItem.query.with_entities(func.sum(FoodItem.quantity)).scalar() or 0
                total_clients = Client.query.count()
                total_volunteers = Volunteer.query.count()
                pending_requests = ClientRequest.query.filter_by(status='Pending').count()
                
                # Get expiring and low stock items
                expiring_items = get_expiring_items(days=7)
                low_stock_items = get_low_stock_items(threshold=10)
                
                # Get recent activity
                recent_requests = ClientRequest.query.order_by(ClientRequest.created_at.desc()).limit(5).all()
                
                # Get today's volunteer schedule
                today = date.today()
                todays_schedule = ScheduleEntry.query.filter_by(date=today).order_by(ScheduleEntry.start_time).all()
                
                # Store all data in a dictionary
                dashboard_data = {
                    'total_inventory': total_inventory,
                    'total_clients': total_clients,
                    'total_volunteers': total_volunteers,
                    'pending_requests': pending_requests,
                    'expiring_items': expiring_items,
                    'low_stock_items': low_stock_items,
                    'recent_requests': recent_requests,
                    'todays_schedule': todays_schedule
                }
                
                # Cache for 5 minutes
                set_cached_data(cache_key, dashboard_data, timeout=300)
            
            # Verify dashboard_data is a dictionary before unpacking
            if not isinstance(dashboard_data, dict):
                # If somehow it's not a dict, create an empty one to avoid errors
                dashboard_data = {}
                
            return render_template('dashboard.html', **dashboard_data)
            
        # Volunteer dashboard
        elif current_user.is_volunteer():
            # Try to get cached dashboard data
            cache_key = f"volunteer_dashboard_{current_user.id}"
            dashboard_data = get_cached_data(cache_key)
            
            if dashboard_data is None:
                volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
                
                # Get upcoming shifts
                upcoming_shifts = []
                if volunteer:
                    upcoming_shifts = ScheduleEntry.query.filter_by(
                        volunteer_id=volunteer.id
                    ).filter(
                        ScheduleEntry.date >= date.today()
                    ).order_by(
                        ScheduleEntry.date, ScheduleEntry.start_time
                    ).limit(10).all()
                
                # Get pantry needs (low stock items)
                pantry_needs = get_low_stock_items(threshold=10)
                
                dashboard_data = {
                    'volunteer': volunteer,
                    'upcoming_shifts': upcoming_shifts,
                    'pantry_needs': pantry_needs
                }
                
                # Cache for 5 minutes
                set_cached_data(cache_key, dashboard_data, timeout=300)
            
            # Verify dashboard_data is a dictionary before unpacking
            if not isinstance(dashboard_data, dict):
                # If somehow it's not a dict, create an empty one to avoid errors
                dashboard_data = {}
                
            return render_template('dashboard.html', **dashboard_data)
            
        # Client dashboard
        elif current_user.is_client():
            # Try to get cached dashboard data
            cache_key = f"client_dashboard_{current_user.id}"
            dashboard_data = get_cached_data(cache_key)
            
            if dashboard_data is None:
                client = Client.query.filter_by(user_id=current_user.id).first()
                
                # Get client requests
                client_requests = []
                if client:
                    client_requests = ClientRequest.query.filter_by(
                        client_id=client.id
                    ).order_by(
                        ClientRequest.created_at.desc()
                    ).all()
                
                dashboard_data = {
                    'client': client,
                    'client_requests': client_requests
                }
                
                # Cache for 5 minutes
                set_cached_data(cache_key, dashboard_data, timeout=300)
            
            # Verify dashboard_data is a dictionary before unpacking
            if not isinstance(dashboard_data, dict):
                # If somehow it's not a dict, create an empty one to avoid errors
                dashboard_data = {}
                
            return render_template('dashboard.html', **dashboard_data)
        
        # Default dashboard
        return render_template('dashboard.html')

    # Inventory routes
    @app.route('/inventory')
    @login_required
    @require_2fa
    @role_required('admin', 'staff', 'volunteer')
    def inventory_index():
        search_form = SearchForm()
        query = request.args.get('query', '')
        category = request.args.get('category', '')
        
        inventory_query = FoodItem.query
        
        if query:
            inventory_query = inventory_query.filter(FoodItem.name.ilike(f'%{query}%'))
        
        if category:
            inventory_query = inventory_query.filter_by(category=category)
            
        inventory = inventory_query.order_by(FoodItem.category, FoodItem.name).all()
        
        # Group items by category
        categories = {}
        for item in inventory:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
            
        return render_template('inventory/index.html', 
            inventory=inventory,
            categories=categories,
            search_form=search_form,
            query=query,
            selected_category=category,
            food_categories=FOOD_CATEGORIES,
            now=datetime.now()
        )

    @app.route('/inventory/add', methods=['GET', 'POST'])
    @login_required
    @require_2fa
    @role_required('admin', 'staff')
    def inventory_add():
        form = FoodItemForm()
        
        if form.validate_on_submit():
            food_item = FoodItem(
                name=form.name.data,
                category=form.category.data,
                quantity=form.quantity.data,
                unit=form.unit.data,
                expiration_date=form.expiration_date.data,
                notes=form.notes.data
            )
            
            db.session.add(food_item)
            db.session.commit()
            
            # Clear inventory-related cache to reflect changes
            from cache import clear_cache
            clear_cache()
            
            flash(f'Added {food_item.quantity} {food_item.unit} of {food_item.name} to inventory.', 'success')
            return redirect(url_for('inventory_index'))
            
        return render_template('inventory/add.html', form=form)

    @app.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('admin', 'staff')
    def inventory_edit(item_id):
        food_item = FoodItem.query.get_or_404(item_id)
        form = FoodItemForm(obj=food_item)
        
        if form.validate_on_submit():
            form.populate_obj(food_item)
            db.session.commit()
            
            # Clear inventory-related cache to reflect changes
            from cache import clear_cache
            clear_cache()
            
            flash(f'Updated inventory for {food_item.name}.', 'success')
            return redirect(url_for('inventory_index'))
            
        return render_template('inventory/edit.html', form=form, item=food_item)

    @app.route('/inventory/delete/<int:item_id>', methods=['POST'])
    @login_required
    @role_required('admin', 'staff')
    def inventory_delete(item_id):
        food_item = FoodItem.query.get_or_404(item_id)
        name = food_item.name
        
        db.session.delete(food_item)
        db.session.commit()
        
        # Clear inventory-related cache to reflect changes
        from cache import clear_cache
        clear_cache()
        
        flash(f'Deleted {name} from inventory.', 'success')
        return redirect(url_for('inventory_index'))

    # Client management routes
    @app.route('/clients')
    @login_required
    @require_2fa
    @role_required('admin', 'staff')
    def clients_index():
        search_query = request.args.get('query', '')
        
        if search_query:
            # Join with User model to search by name or email
            clients = Client.query.join(User).filter(
                (User.full_name.ilike(f'%{search_query}%')) | 
                (User.email.ilike(f'%{search_query}%'))
            ).all()
        else:
            clients = Client.query.all()
            
        return render_template('clients/index.html', clients=clients, search_query=search_query)

    @app.route('/clients/view/<int:client_id>')
    @login_required
    @role_required('admin', 'staff')
    def client_view(client_id):
        client = Client.query.get_or_404(client_id)
        requests = ClientRequest.query.filter_by(client_id=client.id).order_by(ClientRequest.created_at.desc()).all()
        
        return render_template('clients/view.html', client=client, requests=requests)

    @app.route('/clients/edit/<int:client_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('admin', 'staff')
    def client_edit(client_id):
        client = Client.query.get_or_404(client_id)
        form = ClientProfileForm(obj=client)
        
        if form.validate_on_submit():
            form.populate_obj(client)
            db.session.commit()
            
            flash('Client profile updated successfully.', 'success')
            return redirect(url_for('clients_index'))
            
        return render_template('clients/edit.html', form=form, client=client)

    # Client profile routes
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if current_user.is_client():
            client = Client.query.filter_by(user_id=current_user.id).first_or_404()
            form = ClientProfileForm(obj=client)
            
            if form.validate_on_submit():
                form.populate_obj(client)
                db.session.commit()
                
                # Clear cache since client profile updates can affect dashboard
                from cache import clear_cache
                clear_cache()
                
                flash('Your profile has been updated.', 'success')
                return redirect(url_for('dashboard'))
                
            return render_template('clients/edit.html', form=form, client=client, is_profile=True)
            
        elif current_user.is_volunteer():
            volunteer = Volunteer.query.filter_by(user_id=current_user.id).first_or_404()
            form = VolunteerProfileForm(obj=volunteer)
            
            if form.validate_on_submit():
                form.populate_obj(volunteer)
                db.session.commit()
                
                # Clear cache since volunteer profile updates can affect dashboard
                from cache import clear_cache
                clear_cache()
                
                flash('Your profile has been updated.', 'success')
                return redirect(url_for('dashboard'))
                
            return render_template('volunteers/edit.html', form=form, volunteer=volunteer, is_profile=True)
            
        else:
            flash('Profile editing not available for your account type.', 'warning')
            return redirect(url_for('dashboard'))

    # Request routes
    @app.route('/requests')
    @login_required
    @require_2fa
    @role_required('admin', 'staff')
    def requests_index():
        status_filter = request.args.get('status', '')
        
        requests_query = ClientRequest.query
        
        if status_filter:
            requests_query = requests_query.filter_by(status=status_filter)
            
        requests = requests_query.order_by(ClientRequest.created_at.desc()).all()
        
        return render_template('requests/index.html', 
            requests=requests, 
            current_status=status_filter,
            statuses=REQUEST_STATUS
        )

    @app.route('/requests/view/<int:request_id>')
    @login_required
    def request_view(request_id):
        client_request = ClientRequest.query.get_or_404(request_id)
        
        # Check permissions
        if not (current_user.is_admin() or current_user.is_staff()):
            if current_user.is_client():
                client = Client.query.filter_by(user_id=current_user.id).first()
                if not client or client.id != client_request.client_id:
                    flash('You do not have permission to view this request.', 'danger')
                    return redirect(url_for('dashboard'))
            else:
                flash('You do not have permission to view this request.', 'danger')
                return redirect(url_for('dashboard'))
        
        return render_template('requests/view.html', request=client_request)

    @app.route('/requests/add', methods=['GET', 'POST'])
    @login_required
    @role_required('client')
    def request_add():
        # Get client profile
        client = Client.query.filter_by(user_id=current_user.id).first()
        
        # Check if client has completed their profile
        if not client or not client.address:
            flash('Please complete your profile before making a request.', 'warning')
            return redirect(url_for('profile'))
        
        form = ClientRequestForm()
        
        if form.validate_on_submit():
            new_request = ClientRequest(
                client_id=client.id,
                pickup_date=form.pickup_date.data,
                special_notes=form.special_notes.data,
                status='Pending'
            )
            
            db.session.add(new_request)
            db.session.commit()
            
            flash('Your request has been submitted. You can now add items to your request.', 'success')
            return redirect(url_for('request_items_add', request_id=new_request.id))
            
        return render_template('requests/add.html', form=form)

    @app.route('/requests/edit/<int:request_id>', methods=['GET', 'POST'])
    @login_required
    def request_edit(request_id):
        client_request = ClientRequest.query.get_or_404(request_id)
        
        # Check permissions
        if current_user.is_client():
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client or client.id != client_request.client_id:
                flash('You do not have permission to edit this request.', 'danger')
                return redirect(url_for('dashboard'))
                
            # Clients can only edit pending requests
            if client_request.status != 'Pending':
                flash('You cannot edit a request that has already been processed.', 'warning')
                return redirect(url_for('request_view', request_id=request_id))
                
            form = ClientRequestForm(obj=client_request)
            
            if form.validate_on_submit():
                form.populate_obj(client_request)
                db.session.commit()
                
                flash('Your request has been updated.', 'success')
                return redirect(url_for('request_view', request_id=request_id))
                
        elif current_user.is_admin() or current_user.is_staff():
            form = RequestUpdateForm(obj=client_request)
            
            if form.validate_on_submit():
                form.populate_obj(client_request)
                db.session.commit()
                
                flash('Request has been updated.', 'success')
                return redirect(url_for('request_view', request_id=request_id))
                
        else:
            flash('You do not have permission to edit this request.', 'danger')
            return redirect(url_for('dashboard'))
            
        return render_template('requests/edit.html', form=form, request=client_request)

    @app.route('/requests/<int:request_id>/items/add', methods=['GET', 'POST'])
    @login_required
    def request_items_add(request_id):
        client_request = ClientRequest.query.get_or_404(request_id)
        
        # Check permissions
        if current_user.is_client():
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client or client.id != client_request.client_id:
                flash('You do not have permission to edit this request.', 'danger')
                return redirect(url_for('dashboard'))
                
            # Clients can only edit pending requests
            if client_request.status != 'Pending':
                flash('You cannot edit a request that has already been processed.', 'warning')
                return redirect(url_for('request_view', request_id=request_id))
                
        elif not (current_user.is_admin() or current_user.is_staff()):
            flash('You do not have permission to edit this request.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Get available items for the form
        available_items = FoodItem.query.filter(FoodItem.quantity > 0).order_by(FoodItem.category, FoodItem.name).all()
        
        # If no items available, redirect
        if not available_items:
            flash('No items are currently available in inventory.', 'warning')
            return redirect(url_for('request_view', request_id=request_id))
            
        form = RequestItemForm()
        form.food_item_id.choices = [(item.id, f"{item.name} ({item.quantity} {item.unit} available)") for item in available_items]
        
        if form.validate_on_submit():
            # Get the selected food item
            food_item = FoodItem.query.get(form.food_item_id.data)
            
            # Check if quantity requested is available
            if form.quantity_requested.data > food_item.quantity:
                flash(f'Only {food_item.quantity} {food_item.unit} of {food_item.name} available.', 'danger')
                return render_template('requests/items_add.html', form=form, request=client_request)
                
            # Check if item already exists in request
            existing_item = RequestItem.query.filter_by(
                request_id=client_request.id,
                food_item_id=form.food_item_id.data
            ).first()
            
            if existing_item:
                # Update quantity of existing item
                existing_item.quantity_requested += form.quantity_requested.data
                db.session.commit()
                flash(f'Updated quantity for {food_item.name}.', 'success')
            else:
                # Add new item to request
                request_item = RequestItem(
                    request_id=client_request.id,
                    food_item_id=form.food_item_id.data,
                    quantity_requested=form.quantity_requested.data
                )
                
                db.session.add(request_item)
                db.session.commit()
                flash(f'Added {form.quantity_requested.data} {food_item.unit} of {food_item.name} to your request.', 'success')
                
            return redirect(url_for('request_items_add', request_id=request_id))
            
        return render_template('requests/items_add.html', form=form, request=client_request)

    @app.route('/requests/<int:request_id>/items/<int:item_id>/remove', methods=['POST'])
    @login_required
    def request_item_remove(request_id, item_id):
        client_request = ClientRequest.query.get_or_404(request_id)
        request_item = RequestItem.query.get_or_404(item_id)
        
        # Check if item belongs to the request
        if request_item.request_id != client_request.id:
            flash('Invalid request.', 'danger')
            return redirect(url_for('request_view', request_id=request_id))
            
        # Check permissions
        if current_user.is_client():
            client = Client.query.filter_by(user_id=current_user.id).first()
            if not client or client.id != client_request.client_id:
                flash('You do not have permission to edit this request.', 'danger')
                return redirect(url_for('dashboard'))
                
            # Clients can only edit pending requests
            if client_request.status != 'Pending':
                flash('You cannot edit a request that has already been processed.', 'warning')
                return redirect(url_for('request_view', request_id=request_id))
                
        elif not (current_user.is_admin() or current_user.is_staff()):
            flash('You do not have permission to edit this request.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Remove the item
        item_name = request_item.food_item.name if request_item.food_item else 'Unknown item'
        db.session.delete(request_item)
        db.session.commit()
        
        flash(f'Removed {item_name} from the request.', 'success')
        
        if current_user.is_client():
            return redirect(url_for('request_items_add', request_id=request_id))
        else:
            return redirect(url_for('request_view', request_id=request_id))

    @app.route('/requests/<int:request_id>/fulfill', methods=['GET', 'POST'])
    @login_required
    @role_required('admin', 'staff')
    def request_fulfill(request_id):
        client_request = ClientRequest.query.get_or_404(request_id)
        
        # Only pending or approved requests can be fulfilled
        if client_request.status not in ['Pending', 'Approved']:
            flash('This request cannot be fulfilled because it is not pending or approved.', 'warning')
            return redirect(url_for('request_view', request_id=request_id))
            
        if request.method == 'POST':
            # Process each item
            for item in client_request.items:
                item_id = item.id
                quantity_fulfilled = int(request.form.get(f'item_{item_id}_fulfilled', 0))
                
                # Update the item
                item.quantity_fulfilled = quantity_fulfilled
                
                # Update the inventory
                if quantity_fulfilled > 0:
                    food_item = item.food_item
                    if food_item:
                        # Ensure we don't remove more than available
                        actual_fulfilled = min(quantity_fulfilled, food_item.quantity)
                        food_item.quantity -= actual_fulfilled
                        
                        if item.quantity_fulfilled != actual_fulfilled:
                            item.quantity_fulfilled = actual_fulfilled
                            flash(f'Only {actual_fulfilled} of {item.food_item.name} were available.', 'warning')
            
            # Update request status
            client_request.status = 'Completed'
            db.session.commit()
            
            # Clear cache since inventory and requests have changed
            from cache import clear_cache
            clear_cache()
            
            flash('Request has been fulfilled and inventory updated.', 'success')
            return redirect(url_for('requests_index'))
            
        return render_template('requests/fulfill.html', request=client_request)

    # Volunteer management routes
    @app.route('/volunteers')
    @login_required
    @role_required('admin', 'staff')
    def volunteers_index():
        search_query = request.args.get('query', '')
        
        if search_query:
            # Join with User model to search by name or email
            volunteers = Volunteer.query.join(User).filter(
                (User.full_name.ilike(f'%{search_query}%')) | 
                (User.email.ilike(f'%{search_query}%'))
            ).all()
        else:
            volunteers = Volunteer.query.all()
            
        return render_template('volunteers/index.html', volunteers=volunteers, search_query=search_query)

    @app.route('/volunteers/view/<int:volunteer_id>')
    @login_required
    @role_required('admin', 'staff')
    def volunteer_view(volunteer_id):
        volunteer = Volunteer.query.get_or_404(volunteer_id)
        
        # Get upcoming shifts
        upcoming_shifts = ScheduleEntry.query.filter_by(
            volunteer_id=volunteer.id
        ).filter(
            ScheduleEntry.date >= date.today()
        ).order_by(
            ScheduleEntry.date, ScheduleEntry.start_time
        ).all()
        
        # Get past shifts
        past_shifts = ScheduleEntry.query.filter_by(
            volunteer_id=volunteer.id
        ).filter(
            ScheduleEntry.date < date.today()
        ).order_by(
            ScheduleEntry.date.desc(), ScheduleEntry.start_time
        ).limit(10).all()
        
        return render_template('volunteers/view.html', 
            volunteer=volunteer, 
            upcoming_shifts=upcoming_shifts,
            past_shifts=past_shifts
        )

    @app.route('/volunteers/edit/<int:volunteer_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('admin', 'staff')
    def volunteer_edit(volunteer_id):
        volunteer = Volunteer.query.get_or_404(volunteer_id)
        form = VolunteerProfileForm(obj=volunteer)
        
        if form.validate_on_submit():
            form.populate_obj(volunteer)
            db.session.commit()
            
            # Clear cache since volunteer profile updates can affect dashboard
            from cache import clear_cache
            clear_cache()
            
            flash('Volunteer profile updated successfully.', 'success')
            return redirect(url_for('volunteers_index'))
            
        return render_template('volunteers/edit.html', form=form, volunteer=volunteer)

    # Schedule management routes
    @app.route('/schedule')
    @login_required
    @role_required('admin', 'staff', 'volunteer')
    def schedule_index():
        # Get month and year from query parameters or use current month
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        # Get calendar data
        calendar_data = get_month_calendar(year, month)
        
        # Handle potential cache data format issues
        if not isinstance(calendar_data, dict):
            # Clear the specific calendar cache entry
            from cache import clear_specific_cache
            
            # Generate cache key for the calendar
            today = date.today()
            year_val = today.year if year is None else year
            month_val = today.month if month is None else month
            cache_key = f"calendar_{year_val}_{month_val}"
            
            # Clear this specific cache entry
            clear_specific_cache(cache_key)
            
            # Regenerate with validated date
            calendar_data = get_month_calendar(year_val, month_val)
        
        # Get volunteer schedule for the month
        start_date = date(calendar_data['year'], calendar_data['month'], 1)
        if calendar_data['month'] == 12:
            end_date = date(calendar_data['year'] + 1, 1, 1)
        else:
            end_date = date(calendar_data['year'], calendar_data['month'] + 1, 1)
            
        schedule_entries = ScheduleEntry.query.filter(
            ScheduleEntry.date >= start_date,
            ScheduleEntry.date < end_date
        ).order_by(
            ScheduleEntry.date, ScheduleEntry.start_time
        ).all()
        
        # Organize entries by date
        entries_by_date = {}
        for entry in schedule_entries:
            day = entry.date.day
            if day not in entries_by_date:
                entries_by_date[day] = []
            entries_by_date[day].append(entry)
        
        return render_template('schedule/index.html', 
            calendar=calendar_data,
            entries_by_date=entries_by_date
        )

    @app.route('/schedule/day/<int:year>/<int:month>/<int:day>')
    @login_required
    @role_required('admin', 'staff', 'volunteer')
    def schedule_day(year, month, day):
        # Validate inputs
        if year is None or month is None or day is None:
            flash('Invalid date parameters.', 'danger')
            return redirect(url_for('schedule_index'))
        
        # Create the date
        try:
            selected_date = date(year, month, day)
        except ValueError:
            flash('Invalid date.', 'danger')
            return redirect(url_for('schedule_index'))
            
        # Get schedule entries for the day
        entries = ScheduleEntry.query.filter_by(
            date=selected_date
        ).order_by(
            ScheduleEntry.start_time
        ).all()
        
        return render_template('schedule/day.html', 
            selected_date=selected_date,
            entries=entries
        )

    @app.route('/schedule/add', methods=['GET', 'POST'])
    @login_required
    @role_required('admin', 'staff')
    def schedule_add():
        form = ScheduleEntryForm()
        
        # Get date from query parameters if provided
        date_str = request.args.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                form.date.data = selected_date
            except ValueError:
                pass
                
        # Populate volunteer choices
        volunteers = Volunteer.query.join(User).order_by(User.full_name).all()
        form.volunteer_id.choices = [(v.id, v.user.full_name) for v in volunteers]
        form.volunteer_id.choices.insert(0, (0, 'Unassigned'))
        
        if form.validate_on_submit():
            # Check if volunteer_id is valid
            volunteer_id = form.volunteer_id.data if form.volunteer_id.data != 0 else None
            
            schedule_entry = ScheduleEntry(
                volunteer_id=volunteer_id,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                task=form.task.data,
                notes=form.notes.data
            )
            
            db.session.add(schedule_entry)
            db.session.commit()
            
            # Clear cache since schedule entries affect volunteer dashboard
            from cache import clear_cache
            clear_cache()
            
            flash('Schedule entry added successfully.', 'success')
            # Check if date data is valid
            if form.date.data is None:
                flash('Invalid date specified.', 'danger')
                return redirect(url_for('schedule_index'))
                
            return redirect(url_for('schedule_day', 
                year=form.date.data.year,
                month=form.date.data.month,
                day=form.date.data.day
            ))
            
        return render_template('schedule/add.html', form=form)

    @app.route('/schedule/edit/<int:entry_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('admin', 'staff')
    def schedule_edit(entry_id):
        schedule_entry = ScheduleEntry.query.get_or_404(entry_id)
        form = ScheduleEntryForm(obj=schedule_entry)
        
        # Populate volunteer choices
        volunteers = Volunteer.query.join(User).order_by(User.full_name).all()
        form.volunteer_id.choices = [(v.id, v.user.full_name) for v in volunteers]
        form.volunteer_id.choices.insert(0, (0, 'Unassigned'))
        
        if form.validate_on_submit():
            # Check if volunteer_id is valid
            volunteer_id = form.volunteer_id.data if form.volunteer_id.data != 0 else None
            
            schedule_entry.volunteer_id = volunteer_id
            schedule_entry.date = form.date.data
            schedule_entry.start_time = form.start_time.data
            schedule_entry.end_time = form.end_time.data
            schedule_entry.task = form.task.data
            schedule_entry.notes = form.notes.data
            
            db.session.commit()
            
            # Clear cache since schedule entries affect volunteer dashboard
            from cache import clear_cache
            clear_cache()
            
            flash('Schedule entry updated successfully.', 'success')
            # Check if date data is valid
            if schedule_entry.date is None:
                flash('Invalid date specified.', 'danger')
                return redirect(url_for('schedule_index'))
                
            return redirect(url_for('schedule_day', 
                year=schedule_entry.date.year,
                month=schedule_entry.date.month,
                day=schedule_entry.date.day
            ))
            
        return render_template('schedule/edit.html', form=form, entry=schedule_entry)

    @app.route('/schedule/delete/<int:entry_id>', methods=['POST'])
    @login_required
    @role_required('admin', 'staff')
    def schedule_delete(entry_id):
        schedule_entry = ScheduleEntry.query.get_or_404(entry_id)
        entry_date = schedule_entry.date
        
        db.session.delete(schedule_entry)
        db.session.commit()
        
        # Clear cache since schedule entries affect volunteer dashboard
        from cache import clear_cache
        clear_cache()
        
        flash('Schedule entry deleted successfully.', 'success')
        
        # Check if date data is valid
        if entry_date is None:
            flash('Invalid date specified.', 'danger')
            return redirect(url_for('schedule_index'))
            
        return redirect(url_for('schedule_day', 
            year=entry_date.year,
            month=entry_date.month,
            day=entry_date.day
        ))

    # User Management (Admin only)
    @app.route('/users')
    @login_required
    @require_2fa
    @admin_required
    def users_index():
        users = User.query.order_by(User.role, User.username).all()
        return render_template('users/index.html', users=users)

    @app.route('/users/add', methods=['GET', 'POST'])
    @login_required
    @require_2fa
    @admin_required
    def user_add():
        # Check for role parameter in URL
        default_role = request.args.get('role', 'client')
        form = AdminUserCreateForm()
        
        # Set default role from URL parameter
        if not form.is_submitted():
            form.role.data = default_role
        
        if form.validate_on_submit():
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists. Please choose a different one.', 'danger')
                return render_template('users/add.html', form=form)
                
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('users/add.html', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                password_reset_required=True  # Require password change on first login
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            # Create client or volunteer profile based on role
            if user.role == 'client':
                client = Client(user_id=user.id)
                db.session.add(client)
                db.session.commit()
                
            elif user.role == 'volunteer':
                volunteer = Volunteer(user_id=user.id)
                db.session.add(volunteer)
                db.session.commit()
            
            flash(f'User {user.username} created successfully.', 'success')
            return redirect(url_for('users_index'))
            
        return render_template('users/add.html', form=form)

    @app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    @require_2fa
    @admin_required
    def user_edit(user_id):
        user = User.query.get_or_404(user_id)
        form = AdminUserCreateForm(obj=user)
        
        # Remove password field as we don't want to change it automatically
        del form.password
        
        if form.validate_on_submit():
            # Check if username is changed and already exists
            if form.username.data != user.username and User.query.filter_by(username=form.username.data).first():
                flash('Username already exists. Please choose a different one.', 'danger')
                return render_template('users/edit.html', form=form, user=user)
                
            # Check if email is changed and already exists
            if form.email.data != user.email and User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('users/edit.html', form=form, user=user)
            
            # Update user
            user.username = form.username.data
            user.email = form.email.data
            user.full_name = form.full_name.data
            user.phone = form.phone.data
            
            # If role changed, handle related profiles
            if form.role.data != user.role:
                old_role = user.role
                user.role = form.role.data
                
                # Remove old role-specific profile if it exists
                if old_role == 'client':
                    client = Client.query.filter_by(user_id=user.id).first()
                    if client:
                        db.session.delete(client)
                        
                elif old_role == 'volunteer':
                    volunteer = Volunteer.query.filter_by(user_id=user.id).first()
                    if volunteer:
                        db.session.delete(volunteer)
                
                # Create new role-specific profile if needed
                if user.role == 'client' and not Client.query.filter_by(user_id=user.id).first():
                    client = Client(user_id=user.id)
                    db.session.add(client)
                    
                elif user.role == 'volunteer' and not Volunteer.query.filter_by(user_id=user.id).first():
                    volunteer = Volunteer(user_id=user.id)
                    db.session.add(volunteer)
            
            db.session.commit()
            
            # Clear cache since user role changes affect dashboard content
            from cache import clear_cache
            clear_cache()
            
            flash(f'User {user.username} updated successfully.', 'success')
            return redirect(url_for('users_index'))
            
        return render_template('users/edit.html', form=form, user=user)

    @app.route('/users/reset_password/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def user_reset_password(user_id):
        user = User.query.get_or_404(user_id)
        print(f"Password reset requested for user: {user.username}")
        
        # Check if user is authenticated or if this is a password reset after login
        is_from_login = 'password_reset_user_id' in session and session['password_reset_user_id'] == user.id
        
        # Check permissions - only admins, the user themselves, or from login can reset
        if not (current_user.is_authenticated and (current_user.is_admin() or current_user.id == user.id)) and not is_from_login:
            flash('You do not have permission to reset this password.', 'danger')
            return redirect(url_for('login'))
        
        # Use the proper form for password changes
        form = PasswordChangeForm()
        
        # Check if admin is resetting another user's password
        is_admin_reset = current_user.is_authenticated and current_user.is_admin() and current_user.id != user.id
        
        # If admin is resetting another user's password, ensure 2FA is verified
        if is_admin_reset and current_user.otp_enabled and 'otp_verified' not in session:
            session['next'] = url_for('user_reset_password', user_id=user.id)
            flash('Please verify your identity with two-factor authentication before resetting passwords.', 'warning')
            return redirect(url_for('two_factor_verify'))
        print(f"Is admin reset: {is_admin_reset}, Is from login: {is_from_login}, Method: {request.method}")
        
        if request.method == 'POST':
            print(f"Form data received: {form.data}")
            print(f"Form validated: {form.validate()}")
            if form.validate():
                try:
                    # If user is changing their password after it was reset by admin
                    # OR if a regular user is changing their own password
                    if (current_user.is_authenticated and current_user.id == user.id and 
                        (user.password_reset_required or not current_user.is_admin())):
                        # Only validate current password if provided (it's marked optional for admin resets)
                        if form.current_password.data and not user.check_password(form.current_password.data):
                            flash('Current password is incorrect. You must enter the password set by the admin.', 'danger')
                            return render_template('users/reset_password.html', form=form, user=user)
                    # If this is a password reset from the login flow
                    elif is_from_login:
                        # Validate that the temporary password is correct 
                        if not user.check_password(form.current_password.data):
                            flash('Current password is incorrect. You must enter the password set by the admin.', 'danger')
                            return render_template('users/reset_password.html', form=form, user=user)
                    
                    # Validate new password
                    if form.new_password.data != form.confirm_password.data:
                        flash('Passwords do not match.', 'danger')
                        return render_template('users/reset_password.html', form=form, user=user)
                    
                    print(f"Setting new password for {user.username}")
                    # Update password
                    user.set_password(form.new_password.data)
                    
                    # If admin is resetting another user's password, set password_reset_required flag
                    if is_admin_reset:
                        user.password_reset_required = True
                        flash(f'Password for {user.username} has been reset. They will be required to enter this password once before setting their own password.', 'success')
                    else:
                        # User is changing their own password, clear the password reset flag
                        user.password_reset_required = False
                        flash('Your password has been updated successfully.', 'success')
                    
                    db.session.commit()
                    print(f"Password updated successfully for {user.username}")
                    
                    # Redirect based on who's doing the reset
                    if is_admin_reset:
                        return redirect(url_for('users_index'))
                    elif is_from_login:
                        # Clear session var and log the user in
                        session.pop('password_reset_user_id', None)
                        login_user(user)
                        
                        # If 2FA is needed, redirect to setup, otherwise redirect to dashboard
                        if not user.otp_enabled and not user.otp_verified:
                            # Generate a new OTP secret for the user
                            user.generate_otp_secret()
                            db.session.commit()
                            flash('For security reasons, you need to set up two-factor authentication.', 'info')
                            return redirect(url_for('two_factor_setup'))
                        else:
                            flash('Welcome! Your password has been updated.', 'success')
                            return redirect(url_for('dashboard'))
                    else:
                        return redirect(url_for('dashboard'))
                except Exception as e:
                    print(f"Error in password reset: {str(e)}")
                    db.session.rollback()
                    flash(f'An error occurred: {str(e)}', 'danger')
            else:
                for field, errors in form.errors.items():
                    print(f"Validation error in {field}: {', '.join(errors)}")
                    for error in errors:
                        flash(f"{field}: {error}", 'danger')
        
        # For required password changes, show a different message
        if user.password_reset_required and (current_user.is_authenticated and current_user.id == user.id or is_from_login):
            flash('You must enter the temporary password provided by the administrator and then create your own new password.', 'warning')
            
        return render_template('users/reset_password.html', form=form, user=user)

    @app.route('/users/delete/<int:user_id>', methods=['POST'])
    @login_required
    @require_2fa
    @admin_required
    def user_delete(user_id):
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            flash('You cannot delete your own account.', 'danger')
            return redirect(url_for('users_index'))
            
        username = user.username
        
        # Delete user and related data
        db.session.delete(user)
        db.session.commit()
        
        # Clear cache since user data affects various views
        from cache import clear_cache
        clear_cache()
        
        flash(f'User {username} has been deleted.', 'success')
        return redirect(url_for('users_index'))

    # Reports
    @app.route('/reports/inventory')
    @login_required
    @role_required('admin', 'staff')
    def report_inventory():
        # Get inventory by category
        categories = {}
        for item in FoodItem.query.all():
            if item.category not in categories:
                categories[item.category] = {
                    'count': 0,
                    'quantity': 0
                }
            categories[item.category]['count'] += 1
            categories[item.category]['quantity'] += item.quantity
            
        # Get expiring items
        expiring_soon = get_expiring_items(days=30)
        
        # Get low stock items
        low_stock = get_low_stock_items(threshold=10)
        
        return render_template('reports/inventory.html', 
            categories=categories,
            expiring_soon=expiring_soon,
            low_stock=low_stock
        )

    @app.route('/reports/clients')
    @login_required
    @role_required('admin', 'staff')
    def report_clients():
        form = DateRangeForm()
        
        # Default to last 30 days
        start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            
        form.start_date.data = start_date
        form.end_date.data = end_date
        
        # Get client requests in date range
        requests = ClientRequest.query.filter(
            ClientRequest.created_at >= start_date,
            ClientRequest.created_at <= (end_date + timedelta(days=1))  # Include end date
        ).order_by(ClientRequest.created_at).all()
        
        # Count requests by status
        status_counts = {}
        for req in requests:
            if req.status not in status_counts:
                status_counts[req.status] = 0
            status_counts[req.status] += 1
            
        # Count unique clients served
        client_ids = set()
        for req in requests:
            client_ids.add(req.client_id)
        
        return render_template('reports/clients.html', 
            form=form,
            requests=requests,
            status_counts=status_counts,
            unique_clients=len(client_ids),
            start_date=start_date,
            end_date=end_date
        )

    @app.route('/reports/volunteers')
    @login_required
    @role_required('admin', 'staff')
    def report_volunteers():
        form = DateRangeForm()
        
        # Default to last 30 days
        start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            
        form.start_date.data = start_date
        form.end_date.data = end_date
        
        # Get volunteer schedule entries in date range
        schedule_entries = ScheduleEntry.query.filter(
            ScheduleEntry.date >= start_date,
            ScheduleEntry.date <= end_date
        ).order_by(ScheduleEntry.date, ScheduleEntry.start_time).all()
        
        # Count hours by volunteer
        volunteer_hours = {}
        for entry in schedule_entries:
            if not entry.volunteer_id:
                continue
                
            volunteer = Volunteer.query.get(entry.volunteer_id)
            if not volunteer or not volunteer.user:
                continue
                
            # Calculate hours (approximate based on start/end times)
            start_hour = int(entry.start_time.split(':')[0])
            start_am_pm = entry.start_time.split(' ')[1]
            if start_am_pm == 'PM' and start_hour < 12:
                start_hour += 12
                
            end_hour = int(entry.end_time.split(':')[0])
            end_am_pm = entry.end_time.split(' ')[1]
            if end_am_pm == 'PM' and end_hour < 12:
                end_hour += 12
                
            # Handle start/end minutes
            start_minute = int(entry.start_time.split(':')[1].split(' ')[0])
            end_minute = int(entry.end_time.split(':')[1].split(' ')[0])
            
            # Calculate duration in hours
            duration = (end_hour - start_hour) + (end_minute - start_minute) / 60
            
            if volunteer.user.full_name not in volunteer_hours:
                volunteer_hours[volunteer.user.full_name] = 0
                
            volunteer_hours[volunteer.user.full_name] += duration
        
        return render_template('reports/volunteers.html', 
            form=form,
            schedule_entries=schedule_entries,
            volunteer_hours=volunteer_hours,
            start_date=start_date,
            end_date=end_date
        )
