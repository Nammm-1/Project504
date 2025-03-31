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
   pip install -r dependencies.txt
   ```
4. Set up environment variables:
   ```
   export DATABASE_URL="postgresql://username:password@localhost/food_pantry"
   export SESSION_SECRET="your-secret-key"
   ```
5. Initialize the database:
   ```
   python -c "from app import db; db.create_all()"
   ```
6. Start the application:
   ```
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## Project Structure

```
├── app.py                 # Application factory and configuration
├── config.py              # Configuration settings
├── dependencies.txt       # Project dependencies
├── forms.py               # WTForms definitions
├── helpers.py             # Utility functions
├── main.py                # Application entry point
├── models.py              # Database models
├── pyproject.toml         # Project configuration
├── routes.py              # Application routes
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   └── js/                # JavaScript files
└── templates/             # HTML templates
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

## License

[MIT License](LICENSE)

## Credits

Developed by the Replit team for the Food Pantry Management System project.