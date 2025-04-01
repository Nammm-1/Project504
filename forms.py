from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, IntegerField, DateField, TextAreaField, TimeField, SelectMultipleField, SubmitField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
from datetime import date, timedelta
from config import FOOD_CATEGORIES, REQUEST_STATUS, TIME_SLOTS, ROLES

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[Optional()])  # Optional for admin resets
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')
    
    def validate(self):
        print(f"Running PasswordChangeForm validation. Data: {self.data}")
        # First run the standard validators
        if not super().validate():
            print("Failed standard validation")
            for field, errors in self.errors.items():
                print(f"Field {field} errors: {errors}")
            return False
            
        # Check if we need to validate the current password
        from flask import session
        # If this is a password reset from login, current_password is required
        if 'password_reset_user_id' in session:
            print("Validating as password reset from login flow")
            if not self.current_password.data:
                print("Current password not provided")
                self.current_password.errors = ["Current password is required when changing a temporary password."]
                return False
        
        print("Form validation passed")
        return True

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[
        ('client', 'Client'),
        ('volunteer', 'Volunteer')
    ])
    submit = SubmitField('Register')

class AdminUserCreateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('volunteer', 'Volunteer'),
        ('client', 'Client')
    ])
    submit = SubmitField('Create User')

class ClientProfileForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    family_size = IntegerField('Family Size', validators=[DataRequired(), NumberRange(min=1)])
    dietary_restrictions = TextAreaField('Dietary Restrictions or Allergies', validators=[Optional()])
    submit = SubmitField('Save Profile')

class VolunteerProfileForm(FlaskForm):
    skills = TextAreaField('Skills and Experience', validators=[Optional()])
    availability = TextAreaField('General Availability', validators=[Optional()])
    submit = SubmitField('Save Profile')

class FoodItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[(cat, cat) for cat in FOOD_CATEGORIES], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit (e.g., cans, boxes, lbs)', validators=[DataRequired(), Length(max=20)])
    expiration_date = DateField('Expiration Date (if applicable)', validators=[Optional()], format='%Y-%m-%d')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Item')

class ClientRequestForm(FlaskForm):
    pickup_date = DateField('Preferred Pickup Date', validators=[DataRequired()], format='%Y-%m-%d', default=date.today() + timedelta(days=1))
    special_notes = TextAreaField('Special Notes or Requirements', validators=[Optional()])
    submit = SubmitField('Submit Request')

class RequestItemForm(FlaskForm):
    food_item_id = SelectField('Food Item', coerce=int, validators=[DataRequired()])
    quantity_requested = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Item')

class RequestUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[(status, status) for status in REQUEST_STATUS], validators=[DataRequired()])
    pickup_date = DateField('Pickup Date', validators=[Optional()], format='%Y-%m-%d')
    special_notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Update Request')

class RequestItemUpdateForm(FlaskForm):
    request_item_id = HiddenField('Request Item ID')
    quantity_fulfilled = IntegerField('Quantity Fulfilled', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Item')

class ScheduleEntryForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = SelectField('Start Time', choices=[(time, time) for time in TIME_SLOTS[:-1]], validators=[DataRequired()])
    end_time = SelectField('End Time', choices=[(time, time) for time in TIME_SLOTS[1:]], validators=[DataRequired()])
    task = StringField('Task Description', validators=[DataRequired(), Length(max=100)])
    notes = TextAreaField('Notes', validators=[Optional()])
    volunteer_id = SelectField('Volunteer', validators=[Optional()], coerce=lambda x: int(x) if x else None)
    submit = SubmitField('Save Schedule')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional(), Length(max=100)])
    category = SelectField('Category', choices=[('', 'All Categories')] + [(cat, cat) for cat in FOOD_CATEGORIES], validators=[Optional()])
    submit = SubmitField('Search')

class DateRangeForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d', default=date.today() - timedelta(days=30))
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d', default=date.today())
    submit = SubmitField('Generate Report')

class TwoFactorSetupForm(FlaskForm):
    """Form for setting up 2FA"""
    token = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message="Verification code must be 6 digits")
    ])
    submit = SubmitField('Verify and Activate')
    
    def validate_token(self, field):
        # Check if the token is numeric
        if not field.data.isdigit():
            raise ValidationError("Verification code must contain only digits")
            
class TwoFactorVerifyForm(FlaskForm):
    """Form for verifying 2FA code during login"""
    token = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message="Verification code must be 6 digits")
    ])
    remember = BooleanField('Remember this device', default=False)
    submit = SubmitField('Verify')
    
    def validate_token(self, field):
        # Check if the token is numeric
        if not field.data.isdigit():
            raise ValidationError("Verification code must contain only digits")
