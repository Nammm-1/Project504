# Food Pantry Management System

A comprehensive web application for managing local food pantry operations including inventory tracking, client request management, and volunteer coordination.

## Overview

This Food Pantry Management System is designed to streamline the operations of local food pantries by:

- Tracking food inventory and expiration dates
- Managing client registrations and food requests
- Coordinating volunteer schedules
- Generating useful reports and analytics

The system supports four types of users:
- **Administrators**: Complete system access
- **Staff**: Manage day-to-day operations
- **Volunteers**: Access to schedules and assigned tasks
- **Clients**: Request food assistance and manage profiles

## Technologies Used

- **Backend**: Python Flask framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF for form handling and validation
- **Frontend**: Bootstrap CSS framework
- **Deployment**: Gunicorn WSGI server

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirement.txt
   ```
4. Set up environment variables:
   ```
   export DATABASE_URL="postgresql://username:password@localhost/food_pantry"
   export SESSION_SECRET="your-secret-key"
   export DEFAULT_ADMIN_PASSWORD="your-secure-admin-password"  # Optional: Set a custom admin password
   ```
5. Initialize the database:
   ```
   python -c "from app import db; db.create_all()"
   python migrate_db.py      # Add 2FA fields
   python migrate_lockout.py # Add account lockout fields
   ```
6. Start the application:
   ```
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## Project Structure

```
├── app.py                 # Application factory and configuration
├── cache.py               # Caching system utilities
├── config.py              # Configuration settings
├── forms.py               # WTForms definitions
├── helpers.py             # Utility functions
├── logger.py              # Logging system configuration
├── main.py                # Application entry point
├── migrate_db.py          # 2FA database migration script
├── migrate_lockout.py     # Account lockout migration script
├── models.py              # Database models
├── project_report.md      # Comprehensive project report
├── pyproject.toml         # Project configuration
├── requirement.txt        # Project dependencies
├── routes.py              # Application routes
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   └── js/                # JavaScript files
└── templates/             # HTML templates
    ├── auth/              # Authentication templates (2FA, etc.)
    ├── clients/           # Client management templates
    ├── inventory/         # Inventory management templates
    ├── reports/           # Reporting templates
    ├── requests/          # Request management templates
    ├── schedule/          # Volunteer scheduling templates
    ├── users/             # User management templates
    └── volunteers/        # Volunteer management templates
```

## Documentation

For detailed instructions on using and extending the system, refer to:

- [Project Report](./project_report.md): Comprehensive overview of the project
- [User Guide](./user_guide.md): Instructions for end users
- [Technical Documentation](./documentation.md): System architecture and design
- [Technical Reference](./technical_reference.md): Detailed technical specifications

## Features

### Inventory Management
- Add, edit, and track food items
- Monitor quantities and expiration dates
- Categorize items for easy searching

### Client Management
- Register and track client information
- Record family size and dietary restrictions
- Process food assistance requests

### Request Processing
- Multi-step workflow for food requests
- Track item fulfillment and request status
- Manage pickup schedules

### Volunteer Coordination
- Track volunteer skills and availability
- Schedule volunteer shifts
- Assign tasks and track completion

### Reporting
- Generate inventory status reports
- Track client activity and needs
- Monitor volunteer contributions

### User Administration
- Role-based access control
- User account management
- Password reset functionality
- Two-Factor Authentication (2FA) with QR code support
- Account lockout protection after failed login attempts

### Performance Optimization
- Advanced caching system for improved response times
- Database connection pooling with SQLAlchemy
- Optimized queries with proper indexing
- Efficient session management

## License

[MIT License](LICENSE)

## Running in PyCharm

When running this application in PyCharm, follow these additional steps:

1. Import the project into PyCharm
2. Configure a virtual environment (Python Interpreter settings)
3. Install dependencies from the requirement.txt file
4. Configure environment variables in PyCharm:
   - Open **Run** > **Edit Configurations**
   - Add environment variables:
     - DATABASE_URL: Your PostgreSQL connection string
     - SESSION_SECRET: A secure random string
     - DEFAULT_ADMIN_PASSWORD: (Optional) Set a custom admin password
5. Run the application using the PyCharm run button

On first run, the system will automatically create an admin user with:
- Username: `admin`
- Password: Value of DEFAULT_ADMIN_PASSWORD (defaults to "password123" if not set)
- Email: admin@foodpantry.org

Make sure to change this password after first login for security reasons.

