# Food Pantry Management System - Project Report

## Project Overview

The Food Pantry Management System is a comprehensive web application designed to streamline operations for local community food pantries. The system facilitates efficient inventory management, client request handling, volunteer scheduling, and administrative tasks. Specifically built to operate in a local PyCharm environment, the application prioritizes ease of use for staff, volunteers, and clients.

## Key Features

### User Authentication and Security
- Multi-role user authentication (Admin, Staff, Volunteer, Client)
- Enhanced Two-Factor Authentication (2FA) with QR code support and manual entry option
- Password reset workflow with forced password change for admin-created accounts only
- Account lockout mechanism after 3 failed login attempts (30-second timeout with countdown display)
- Role-based access control throughout the application
- Secure session management with proper timeouts

### Inventory Management
- Real-time tracking of food items with categories, quantities, and expiration dates
- Low stock alerts and expiring item notifications
- Streamlined inventory addition and update interface
- Inventory search and filtering capabilities

### Client Management
- Client self-registration and profile management
- Demographic information collection for reporting
- Family size and dietary restriction tracking
- Client request system for food assistance

### Food Request Processing
- Multi-stage request workflow (Pending, Approved, Ready, Completed, Cancelled)
- Item-level request management with quantity control
- Pickup date scheduling and request notes
- Automated inventory deduction upon request fulfillment

### Volunteer Scheduling
- Shift management with date and time slot selection
- Task assignment and tracking
- Volunteer availability recording
- Schedule visualization by day, week, and month

### Reporting and Analytics
- Inventory usage reports with date range filtering
- Client demographic summaries
- Volunteer activity tracking
- System usage statistics

### System Performance
- Advanced caching system with type checking and validation
- Optimized database queries using SQLAlchemy with connection pooling
- Fast response times even with large datasets
- Efficient session management to minimize database interactions

## Technical Implementation

### Architecture
- Python Flask web framework (version 3.1.0+)
- PostgreSQL database with SQLAlchemy ORM (version 2.0.39+)
- Responsive Bootstrap-based UI with dark theme for comfortable viewing
- Modular code organization with separation of concerns
- PyOTP and QRCode libraries for secure two-factor authentication

### Security Features
- Proper password hashing using Werkzeug security
- CSRF protection using Flask-WTF on all forms
- Session management with Flask-Login
- Input validation and sanitization on both client and server side
- Secure cookie handling with HTTPOnly flags
- Account lockout mechanism with automatic unlocking after timeout
- Two-factor authentication with both QR code and manual entry support

### Code Organization
- Modular application structure
- Separation of routes, models, forms, and helpers
- Custom decorators for access control and 2FA enforcement
- Optimized logging system for security events and user activity
- Cache management utilities for performance optimization

## Future Enhancements

Potential areas for future development include:

1. Donation tracking and donor management
2. Barcode scanning for inventory management
3. Integration with external food bank databases
4. Mobile application for volunteers and clients
5. Automated email/SMS notifications for clients and volunteers
6. Advanced analytics and reporting dashboard
7. Integration with community partner organizations

## Deployment Considerations

The application is designed to run:
- Locally using PyCharm IDE
- On a local network for small to medium-sized food pantries
- With minimal server requirements (Python 3.x, PostgreSQL)

## User Guide

### Admin Setup
1. Default admin credentials: username `admin`, password `password123`
2. Set up 2FA on first login using the QR code or manual entry option
3. Create staff and volunteer accounts as needed (these will require password reset on first login)
4. Set up initial inventory categories and items
5. Configure volunteer schedules and manage user access

### Staff Operations
1. Process and fulfill client requests through the request management interface
2. Manage inventory levels and receive alerts about expiring or low-stock items
3. Create and manage volunteer schedules with or without assigned volunteers
4. Register clients directly from the dashboard and assist with food request submissions
5. View reports on inventory, client activity, and volunteer contributions

### Volunteer Activities
1. View assigned schedules and upcoming shifts
2. Assist with inventory management by recording donations and updates
3. Help process client requests by preparing food packages
4. Update volunteer profile with skills and availability information
5. Complete 2FA setup for account security

### Client Usage
1. Register for a self-service account (no forced password reset required)
2. Complete profile with family information and dietary restrictions
3. Submit food assistance requests with specific items needed
4. View request status and history to track assistance
5. Update personal information as needed

## Conclusion

The Food Pantry Management System provides a comprehensive solution for food pantry operations, focusing on usability, efficiency, and security. The system is designed to streamline administrative tasks, improve inventory management, and enhance the experience for both staff and clients.

The application emphasizes ease of use for all stakeholders, including elderly users and volunteers with varying levels of technical expertise. By digitizing and centralizing food pantry operations, the system helps organizations serve their communities more effectively while maintaining accurate records for reporting and planning purposes.

Recent enhancements to the system include:
1. Enhanced Two-Factor Authentication with QR code scanning and manual entry options
2. Improved password management workflow that only requires password resets for admin-created accounts
3. Account lockout mechanism with 30-second timeout after three failed login attempts
4. Advanced caching system for improved performance
5. Ability to register clients directly from the dashboard
6. Enhanced volunteer scheduling that supports assignments without volunteers
7. Improved security with session-based verification flows

The local deployment model using PyCharm ensures that the application can be used by small to medium-sized food pantries without complex infrastructure requirements, while still maintaining robust security and performance characteristics.