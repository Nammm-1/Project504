# Food Pantry Management System - Technical Reference

This document provides detailed technical information for developers working on the Food Pantry Management System.

## Application Architecture

The application follows a Model-View-Controller (MVC) pattern:
- **Models** (models.py): Database schema definitions
- **Views** (templates): HTML templates with Jinja2
- **Controllers** (routes.py): Route handlers and business logic

## Database Tables Schema Details

### User Table
```
+----------------+-------------+------+-----+---------+----------------+
| Field                | Type        | Null | Key | Default | Extra          |
+---------------------+-------------+------+-----+---------+----------------+
| id                  | INTEGER     | NO   | PRI | NULL    | auto_increment |
| username            | VARCHAR(64) | NO   | UNI | NULL    |                |
| email               | VARCHAR(120)| NO   | UNI | NULL    |                |
| password_hash       | VARCHAR(256)| NO   |     | NULL    |                |
| role                | VARCHAR(20) | NO   |     | NULL    |                |
| full_name           | VARCHAR(100)| YES  |     | NULL    |                |
| phone               | VARCHAR(20) | YES  |     | NULL    |                |
| created_at          | DATETIME    | YES  |     | NOW()   |                |
| password_reset_required | BOOLEAN | YES  |     | FALSE   |                |
| otp_secret          | VARCHAR(32) | YES  |     | NULL    |                |
| otp_enabled         | BOOLEAN     | YES  |     | FALSE   |                |
| otp_verified        | BOOLEAN     | YES  |     | FALSE   |                |
+----------------+-------------+------+-----+---------+----------------+
```

### FoodItem Table
```
+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | INTEGER     | NO   | PRI | NULL    | auto_increment |
| name           | VARCHAR(100)| NO   |     | NULL    |                |
| category       | VARCHAR(50) | NO   |     | NULL    |                |
| quantity       | INTEGER     | YES  |     | 0       |                |
| unit           | VARCHAR(20) | YES  |     | 'item'  |                |
| expiration_date| DATE        | YES  |     | NULL    |                |
| notes          | TEXT        | YES  |     | NULL    |                |
| created_at     | DATETIME    | YES  |     | NOW()   |                |
| updated_at     | DATETIME    | YES  |     | NOW()   |                |
+----------------+-------------+------+-----+---------+----------------+
```

### Client Table
```
+---------------------+-------------+------+-----+---------+----------------+
| Field               | Type        | Null | Key | Default | Extra          |
+---------------------+-------------+------+-----+---------+----------------+
| id                  | INTEGER     | NO   | PRI | NULL    | auto_increment |
| user_id             | INTEGER     | NO   | FK  | NULL    |                |
| address             | VARCHAR(200)| YES  |     | NULL    |                |
| family_size         | INTEGER     | YES  |     | 1       |                |
| dietary_restrictions| TEXT        | YES  |     | NULL    |                |
| created_at          | DATETIME    | YES  |     | NOW()   |                |
| updated_at          | DATETIME    | YES  |     | NOW()   |                |
+---------------------+-------------+------+-----+---------+----------------+
```

### ClientRequest Table
```
+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | INTEGER     | NO   | PRI | NULL    | auto_increment |
| client_id      | INTEGER     | NO   | FK  | NULL    |                |
| status         | VARCHAR(20) | YES  |     | 'Pending'|               |
| pickup_date    | DATE        | YES  |     | NULL    |                |
| special_notes  | TEXT        | YES  |     | NULL    |                |
| created_at     | DATETIME    | YES  |     | NOW()   |                |
| updated_at     | DATETIME    | YES  |     | NOW()   |                |
+----------------+-------------+------+-----+---------+----------------+
```

### RequestItem Table
```
+-------------------+-------------+------+-----+---------+----------------+
| Field             | Type        | Null | Key | Default | Extra          |
+-------------------+-------------+------+-----+---------+----------------+
| id                | INTEGER     | NO   | PRI | NULL    | auto_increment |
| request_id        | INTEGER     | NO   | FK  | NULL    |                |
| food_item_id      | INTEGER     | NO   | FK  | NULL    |                |
| quantity_requested| INTEGER     | YES  |     | 1       |                |
| quantity_fulfilled| INTEGER     | YES  |     | 0       |                |
+-------------------+-------------+------+-----+---------+----------------+
```

### Volunteer Table
```
+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | INTEGER     | NO   | PRI | NULL    | auto_increment |
| user_id        | INTEGER     | NO   | FK  | NULL    |                |
| skills         | TEXT        | YES  |     | NULL    |                |
| availability   | TEXT        | YES  |     | NULL    |                |
| created_at     | DATETIME    | YES  |     | NOW()   |                |
| updated_at     | DATETIME    | YES  |     | NOW()   |                |
+----------------+-------------+------+-----+---------+----------------+
```

### ScheduleEntry Table
```
+----------------+-------------+------+-----+---------+----------------+
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | INTEGER     | NO   | PRI | NULL    | auto_increment |
| volunteer_id   | INTEGER     | NO   | FK  | NULL    |                |
| date           | DATE        | NO   |     | NULL    |                |
| start_time     | VARCHAR(10) | NO   |     | NULL    |                |
| end_time       | VARCHAR(10) | NO   |     | NULL    |                |
| task           | VARCHAR(100)| NO   |     | NULL    |                |
| notes          | TEXT        | YES  |     | NULL    |                |
| created_at     | DATETIME    | YES  |     | NOW()   |                |
| updated_at     | DATETIME    | YES  |     | NOW()   |                |
+----------------+-------------+------+-----+---------+----------------+
```

## Role-Based Access Control Details

### Permission Matrix

| Feature                  | Admin | Staff | Volunteer | Client |
|--------------------------|-------|-------|-----------|--------|
| User Management          | ✅    | ❌    | ❌        | ❌     |
| Staff Assignment         | ✅    | ❌    | ❌        | ❌     |
| Inventory Management     | ✅    | ✅    | ❌        | ❌     |
| Client Management        | ✅    | ✅    | ❌        | ❌     |
| View Client Details      | ✅    | ✅    | ❌        | Self   |
| Request Management       | ✅    | ✅    | ❌        | Self   |
| Request Creation         | ✅    | ✅    | ❌        | ✅     |
| Request Fulfillment      | ✅    | ✅    | ❌        | ❌     |
| Volunteer Management     | ✅    | ✅    | ❌        | ❌     |
| Schedule Management      | ✅    | ✅    | View      | ❌     |
| Reports/Analytics        | ✅    | ✅    | ❌        | ❌     |

## Route Structure Details

### Authentication Routes
- `/login` - User login (GET, POST)
- `/logout` - User logout (GET)
- `/register` - New user registration (GET, POST)
- `/2fa/setup` - Set up two-factor authentication (GET, POST)
- `/2fa/verify` - Verify two-factor authentication code (GET, POST)

### Dashboard Routes
- `/` - Main landing page (GET)
- `/dashboard` - User dashboard based on role (GET)

### Inventory Routes
- `/inventory` - List all inventory items (GET)
- `/inventory/add` - Add new inventory item (GET, POST)
- `/inventory/edit/<id>` - Edit existing item (GET, POST)
- `/inventory/delete/<id>` - Delete inventory item (POST)

### Client Routes
- `/clients` - List all clients (GET)
- `/clients/view/<id>` - View client details (GET)
- `/clients/edit/<id>` - Edit client information (GET, POST)
- `/profile` - Edit own profile (GET, POST)

### Request Routes
- `/requests` - List all requests (GET)
- `/requests/view/<id>` - View request details (GET)
- `/requests/add` - Create new request (GET, POST)
- `/requests/edit/<id>` - Edit request (GET, POST)
- `/requests/<id>/items/add` - Add items to request (GET, POST)
- `/requests/<id>/items/<item_id>/remove` - Remove item from request (POST)
- `/requests/<id>/fulfill` - Process/fulfill request (GET, POST)

### Volunteer Routes
- `/volunteers` - List all volunteers (GET)
- `/volunteers/view/<id>` - View volunteer details (GET)
- `/volunteers/edit/<id>` - Edit volunteer information (GET, POST)

### Schedule Routes
- `/schedule` - View schedule calendar (GET)
- `/schedule/day/<year>/<month>/<day>` - View schedule for specific day (GET)
- `/schedule/add` - Add new schedule entry (GET, POST)
- `/schedule/edit/<id>` - Edit schedule entry (GET, POST)
- `/schedule/delete/<id>` - Delete schedule entry (POST)

### User Routes
- `/users` - List all users (GET)
- `/users/add` - Add new user (GET, POST)
- `/users/edit/<id>` - Edit user (GET, POST)
- `/users/reset-password/<id>` - Reset user password (GET, POST)
- `/users/delete/<id>` - Delete user (POST)

### Report Routes
- `/reports/inventory` - Inventory reports (GET, POST)
- `/reports/clients` - Client activity reports (GET, POST)
- `/reports/volunteers` - Volunteer hour reports (GET, POST)

## Form Configuration Details

### Login Form
```python
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
```

### Registration Form
```python
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[
        ('client', 'Client'),
        ('volunteer', 'Volunteer')
    ])
    submit = SubmitField('Register')
```

### Two-Factor Authentication Setup Form
```python
class TwoFactorSetupForm(FlaskForm):
    token = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message="Verification code must be 6 digits")
    ])
    submit = SubmitField('Verify and Activate')
```

### Two-Factor Authentication Verification Form
```python
class TwoFactorVerifyForm(FlaskForm):
    token = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message="Verification code must be 6 digits")
    ])
    remember = BooleanField('Remember this device', default=False)
    submit = SubmitField('Verify')
```

## Template Inheritance Structure

```
base.html
├── index.html
├── login.html
├── register.html
├── dashboard.html
├── inventory/*.html
│   ├── index.html
│   ├── add.html
│   └── edit.html
├── clients/*.html
│   ├── index.html
│   ├── view.html
│   └── edit.html
├── requests/*.html
│   ├── index.html
│   ├── view.html
│   ├── add.html
│   ├── edit.html
│   ├── items_add.html
│   └── fulfill.html
├── volunteers/*.html
│   ├── index.html
│   ├── view.html
│   └── edit.html
├── schedule/*.html
│   ├── index.html
│   ├── day.html
│   ├── add.html
│   └── edit.html
├── users/*.html
│   ├── index.html
│   ├── add.html
│   ├── edit.html
│   └── reset_password.html
└── reports/*.html
    ├── inventory.html
    ├── clients.html
    └── volunteers.html
```

## Application Initialization Sequence

1. **app.py**: Create Flask application
   - Initialize Flask extensions (SQLAlchemy, LoginManager)
   - Load configuration from config.py
   - Setup database connection
   - Import models and create tables
   - Register routes

2. **main.py**: Run application
   - Import Flask app from app.py
   - Run with Gunicorn configuration

## API Endpoints for Chart.js Data

These endpoints return JSON data for Chart.js visualizations:

1. `/api/inventory/categories` - Inventory distribution by category
2. `/api/requests/status` - Request status distribution
3. `/api/volunteers/hours` - Volunteer hours by volunteer
4. `/api/requests/trend` - Request trend over time

## Database Query Optimization

Key queries that may require optimization:
- Inventory items nearing expiration
- Low stock inventory alerts
- Client request history
- Volunteer schedule availability

## Security Implementations

### Two-Factor Authentication (2FA)

The application implements Time-based One-Time Password (TOTP) two-factor authentication using the PyOTP library:

1. **Setup Process**:
   - On first login or when requested, a TOTP secret is generated for the user
   - A QR code is displayed for scanning with authenticator apps (Google Authenticator, Authy, etc.)
   - User verifies setup by entering a valid TOTP code
   - User's account is marked with `otp_enabled` and `otp_verified` flags

2. **Verification Process**:
   - After password verification, users with enabled 2FA are redirected to verification
   - Users enter the 6-digit TOTP code from their authenticator app
   - Optional "remember this device" feature using secure cookies

3. **Security Enforcement**:
   - Critical admin routes are protected with `@require_2fa` decorator
   - User management functions (add, edit, delete) require 2FA verification
   - Password reset operations for other users require 2FA verification
   - Session-based 2FA state management for security

4. **Recovery Options**:
   - Admins can reset 2FA for users if needed
   - Backup codes feature planned for future implementation

### Password Security

1. **Hashing**: Passwords are securely hashed using Werkzeug's `generate_password_hash` function
2. **Reset Workflow**: Customized for admin-created vs. self-registered accounts
3. **Forced Reset**: Admin-created accounts require password change on first login

## Security Implementation Details

### Account Lockout Mechanism

The account lockout mechanism is implemented in the User model with the following fields:
- `failed_login_attempts`: Tracks consecutive failed login attempts
- `lockout_until`: Timestamp until which the account is locked
- `last_failed_login`: Timestamp of the last failed login attempt

The lockout process works as follows:
1. On each failed login attempt, `failed_login_attempts` is incremented
2. When `failed_login_attempts` reaches 3, `lockout_until` is set to the current time + 30 seconds
3. During the lockout period, login attempts are rejected with a countdown timer displayed
4. After the lockout period expires, users can attempt to login again
5. On successful login, `failed_login_attempts` is reset to 0

Code in the login route checks the lockout status before validating credentials:
```python
# Check if account is locked
if user.is_locked_out():
    remaining_seconds = user.get_lockout_remaining_seconds()
    flash(f'Account is temporarily locked. Please try again in {remaining_seconds} seconds.', 'danger')
    return redirect(url_for('login'))
```

### Two-Factor Authentication

Two-Factor Authentication is implemented using PyOTP and QRCode libraries:

1. **Database Fields in User Model**:
   - `otp_secret`: Stores the TOTP secret key
   - `otp_enabled`: Boolean flag indicating if 2FA is enabled
   - `otp_verified`: Boolean flag indicating if 2FA setup is completed

2. **Setup Process**:
   - When a user needs to set up 2FA, a random secret is generated and stored:
     ```python
     user.otp_secret = pyotp.random_base32()
     user.otp_enabled = True
     user.otp_verified = False
     ```
   - A QR code is generated for the user to scan:
     ```python
     totp = pyotp.TOTP(user.otp_secret)
     provisioning_uri = totp.provisioning_uri(user.email, issuer_name="Food Pantry System")
     qr = qrcode.make(provisioning_uri)
     # Save QR code image for display
     ```
   - User verifies by entering a valid TOTP code, which sets `otp_verified = True`

3. **Verification Process**:
   - After password login, users with `otp_enabled=True` are redirected to 2FA verification
   - User enters the 6-digit code from their authenticator app
   - Code is verified against the stored secret:
     ```python
     totp = pyotp.TOTP(user.otp_secret)
     if totp.verify(token):
         # Authentication successful
     ```

4. **Session Management**:
   - 2FA status is tracked in the session:
     ```python
     session['needs_2fa_verification'] = True
     # After successful verification:
     session['needs_2fa_verification'] = False
     session['2fa_verified'] = True
     ```

5. **Enforcement**:
   - Critical routes are protected with a decorator that checks 2FA verification:
     ```python
     @require_2fa
     def admin_only_route():
         # Protected functionality
     ```

## Error Handling and Logging

The application uses Flask's built-in error handling with custom error pages:
- 404 - Not Found
- 403 - Forbidden
- 500 - Internal Server Error

Logging is configured at DEBUG level to assist with development, with additional security-specific logging for authentication events and user actions.

## Development Environment Setup

1. Clone the repository
2. Set up a virtual environment
3. Install dependencies
4. Configure environment variables
   - DATABASE_URL
   - SESSION_SECRET
5. Run database migrations
6. Start the development server

## Production Deployment Considerations

1. Set DEBUG=False in production
2. Use a robust SECRET_KEY
3. Properly configure database connection pooling
4. Set up proper logging
5. Configure Gunicorn with appropriate workers
6. Consider using a reverse proxy (Nginx/Apache)
7. Set up regular database backups

## Testing Strategy

The application should be tested with:
1. Unit tests for models and helper functions
2. Integration tests for routes and form handling
3. End-to-end tests for user workflows

## Coding Standards

This project follows PEP 8 Python style guidelines with these specifics:
- 4 spaces for indentation
- Maximum line length of 100 characters
- docstrings for all functions and classes
- Clear variable and function naming
- Appropriate use of comments

## Contributors and Maintainers

This documentation is intended for developers working on the Food Pantry Management System.