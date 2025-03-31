# Food Pantry Management System Documentation

## System Overview

The Food Pantry Management System is a web-based application designed to help local food pantries efficiently manage inventory, client requests, volunteer scheduling, and reporting. The system streamlines the process of food donation intake, distribution, and volunteer coordination to better serve community members in need.

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login for session management and authentication
- **Forms**: Flask-WTF for form handling and validation
- **Templating**: Jinja2 (integrated with Flask)
- **Frontend**: Bootstrap CSS framework with Replit dark theme
- **Server**: Gunicorn for production deployment

## Application Structure

### Core Files

1. **main.py**: Entry point that runs the Flask application
2. **app.py**: Application factory and configuration setup
3. **config.py**: Configuration variables and settings
4. **models.py**: Database models/schema definitions
5. **forms.py**: Form classes for data validation and collection
6. **routes.py**: All application routes/endpoints
7. **helpers.py**: Utility functions and helper methods

### Directory Structure

```
├── static/               # Static assets
│   ├── css/              # CSS stylesheets
│   └── js/               # JavaScript files
├── templates/            # HTML templates
│   ├── clients/          # Client management templates
│   ├── inventory/        # Inventory management templates
│   ├── reports/          # Reporting templates
│   ├── requests/         # Request management templates
│   ├── schedule/         # Volunteer scheduling templates
│   ├── users/            # User management templates
│   ├── volunteers/       # Volunteer management templates
│   └── base.html         # Base template extended by others
└── [core python files]   # main.py, app.py, models.py, etc.
```

## Database Schema

The application uses a relational database with the following key models:

### User Model
Central authentication and user management model with roles.

- **Attributes**: id, username, email, password_hash, role, full_name, phone, created_at
- **Relationships**: 
  - One-to-one with Client (for client role)
  - One-to-one with Volunteer (for volunteer role)
- **Methods**:
  - set_password(): Hashes and stores a user password
  - check_password(): Verifies a password against stored hash
  - is_admin(), is_staff(), is_volunteer(), is_client(): Role checking

### FoodItem Model
Represents food inventory items in the pantry.

- **Attributes**: id, name, category, quantity, unit, expiration_date, notes, created_at, updated_at
- **Relationships**: One-to-many with RequestItem

### Client Model
Represents users receiving food assistance.

- **Attributes**: id, user_id, address, family_size, dietary_restrictions, created_at, updated_at
- **Relationships**: 
  - One-to-one with User
  - One-to-many with ClientRequest

### ClientRequest Model
Food requests submitted by clients.

- **Attributes**: id, client_id, status, pickup_date, special_notes, created_at, updated_at
- **Relationships**: One-to-many with RequestItem

### RequestItem Model
Many-to-many relationship between ClientRequest and FoodItem.

- **Attributes**: id, request_id, food_item_id, quantity_requested, quantity_fulfilled
- **Relationships**:
  - Many-to-one with ClientRequest
  - Many-to-one with FoodItem

### Volunteer Model
Represents pantry volunteers.

- **Attributes**: id, user_id, skills, availability, created_at, updated_at
- **Relationships**:
  - One-to-one with User
  - One-to-many with ScheduleEntry

### ScheduleEntry Model
Volunteer schedule and task assignments.

- **Attributes**: id, volunteer_id, date, start_time, end_time, task, notes, created_at, updated_at
- **Relationships**: Many-to-one with Volunteer

## Authentication and Authorization

The system implements role-based access control with four primary roles:

1. **Admin**: Full system access, can manage users, inventory, clients, volunteers, and reports
2. **Staff**: Can manage inventory, client requests, and volunteers
3. **Volunteer**: Limited access to schedule and assigned tasks
4. **Client**: Can view and submit food requests, view their profile

Authorization is enforced through decorators:
- `@admin_required`: Limits access to admin users
- `@staff_required`: Limits access to staff and admin users
- `@role_required(*roles)`: Generic decorator that accepts a list of allowed roles

## Key Features

### User Management
- Registration and authentication
- Role-based access control
- User profile management

### Inventory Management
- Add, edit, and remove food items
- Track quantities and expiration dates
- Categorize food items

### Client Management
- Register and manage client information
- Track family size and dietary restrictions
- View client request history

### Request Processing
- Clients can submit food requests
- Staff can review and fulfill requests
- Multi-step workflow (Pending → Approved → In Progress → Completed)

### Volunteer Coordination
- Manage volunteer profiles and availability
- Schedule volunteer shifts
- Assign tasks to volunteers

### Reporting
- Inventory status reports
- Client activity reports
- Volunteer hour tracking

## Form System

The application uses WTForms to handle data validation and collection:

- **LoginForm**: User authentication
- **RegistrationForm**: New user registration
- **AdminUserCreateForm**: Create users with admin privileges
- **ClientProfileForm**: Manage client-specific information
- **VolunteerProfileForm**: Manage volunteer-specific information
- **FoodItemForm**: Add/edit inventory items
- **ClientRequestForm**: Submit new food requests
- **RequestItemForm**: Add items to a request
- **RequestUpdateForm**: Update request status
- **ScheduleEntryForm**: Manage volunteer schedules
- **SearchForm**: Search functionality
- **DateRangeForm**: Date-range selection for reports

## Route Structure

The application is organized into several route groups:

1. **Authentication routes**: Login, logout, registration
2. **Dashboard routes**: Main dashboard, summary views
3. **Inventory routes**: Manage food inventory
4. **Client routes**: Client management
5. **Request routes**: Food request management
6. **Volunteer routes**: Volunteer management
7. **Schedule routes**: Volunteer schedule management
8. **User routes**: User administration
9. **Report routes**: System reports and analytics

## Helper Functions

Various utility functions assist with common tasks:

- **role_required, admin_required, staff_required**: Access control decorators
- **get_upcoming_week_dates**: Calendar helper for scheduling
- **format_date, format_datetime**: Date formatting utilities
- **get_expiring_items**: Find inventory nearing expiration
- **get_low_stock_items**: Find low inventory items

## Configuration

The system uses a configuration file (config.py) with these key settings:

- **DATABASE_URL**: Database connection string
- **SECRET_KEY**: Session security key
- **ROLES**: Defined user roles
- **FOOD_CATEGORIES**: Predefined food categories
- **REQUEST_STATUS**: Possible status values for requests
- **TIME_SLOTS**: Available time slots for scheduling

## JavaScript Utilities

The application includes several client-side utilities:

- **chart-utils.js**: Data visualization for reports
  - createInventoryChart: Display inventory distribution
  - createRequestStatusChart: Show request status breakdown
  - createVolunteerHoursChart: Visualize volunteer contributions
  - createRequestTrendChart: Track requests over time

- **scripts.js**: General-purpose utilities
  - convertTo24Hour: Time format conversion for scheduling

## Deployment

The application is configured to run with Gunicorn for production deployment:
- Binds to all interfaces (0.0.0.0) on port 5000
- Enables automatic reloading during development

## Setup Instructions

### General Setup

1. Ensure Python 3.x is installed
2. Install required packages: `pip install -r dependencies.txt`
3. Set up PostgreSQL database and configure DATABASE_URL
4. Set SESSION_SECRET environment variable
5. Optionally set DEFAULT_ADMIN_PASSWORD environment variable
6. Run database migrations: `python -c "from app import db; db.create_all()"`
7. Start the application: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

### PyCharm-Specific Setup

For those using PyCharm IDE, follow these additional configuration steps:

1. **Import Project**:
   - Open PyCharm and select "Open" to navigate to the project folder
   - Select the root directory of the project

2. **Configure Python Interpreter**:
   - Go to File > Settings > Project > Python Interpreter
   - Create a new virtual environment or select an existing one
   - Install dependencies: In the terminal, run `pip install -r dependencies.txt`

3. **Configure Environment Variables**:
   - Go to Run > Edit Configurations
   - Select "+" to create a new configuration
   - Choose "Python" as the configuration type
   - Set the script path to point to `main.py`
   - In the "Environment variables" field, add:
     ```
     DATABASE_URL=postgresql://username:password@localhost/food_pantry;SESSION_SECRET=your-secret-key;DEFAULT_ADMIN_PASSWORD=your-admin-password
     ```

4. **Configure Database**:
   - Install PostgreSQL if not already installed
   - Create a new database named "food_pantry" (or your preferred name)
   - Update the DATABASE_URL environment variable with your connection details

5. **Run the Application**:
   - Click the Run button (green triangle) in PyCharm
   - The application will start and create an admin user if none exists
   - Default admin credentials:
     - Username: admin
     - Password: value of DEFAULT_ADMIN_PASSWORD (defaults to "password123" if not set)

6. **Access the Application**:
   - Open a web browser and navigate to http://localhost:5000
   - Log in with the admin credentials

## Security Considerations

- Passwords are hashed using Werkzeug's security functions
- Session data is protected with a secret key
- SQL injection protection through ORM (SQLAlchemy)
- CSRF protection on all forms via Flask-WTF