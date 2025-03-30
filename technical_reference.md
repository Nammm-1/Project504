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
| Field          | Type        | Null | Key | Default | Extra          |
+----------------+-------------+------+-----+---------+----------------+
| id             | INTEGER     | NO   | PRI | NULL    | auto_increment |
| username       | VARCHAR(64) | NO   | UNI | NULL    |                |
| email          | VARCHAR(120)| NO   | UNI | NULL    |                |
| password_hash  | VARCHAR(256)| NO   |     | NULL    |                |
| role           | VARCHAR(20) | NO   |     | NULL    |                |
| full_name      | VARCHAR(100)| YES  |     | NULL    |                |
| phone          | VARCHAR(20) | YES  |     | NULL    |                |
| created_at     | DATETIME    | YES  |     | NOW()   |                |
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

## Error Handling and Logging

The application uses Flask's built-in error handling with custom error pages:
- 404 - Not Found
- 403 - Forbidden
- 500 - Internal Server Error

Logging is configured at DEBUG level to assist with development.

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