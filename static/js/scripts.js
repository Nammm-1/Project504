// Food Pantry Management System - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle request item deletion confirmation
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Handle request fulfillment quantity adjustments
    const fulfillmentForm = document.getElementById('fulfillment-form');
    if (fulfillmentForm) {
        const quantityInputs = fulfillmentForm.querySelectorAll('input[type="number"]');
        quantityInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                const max = parseInt(this.getAttribute('max'), 10);
                const value = parseInt(this.value, 10);
                
                if (value > max) {
                    this.value = max;
                    alert(`Only ${max} items are available in inventory.`);
                }
                
                if (value < 0) {
                    this.value = 0;
                }
            });
        });
    }

    // Handle schedule entry form time validation
    const scheduleForm = document.querySelector('form.schedule-form');
    if (scheduleForm) {
        scheduleForm.addEventListener('submit', function(e) {
            const startTime = document.getElementById('start_time').value;
            const endTime = document.getElementById('end_time').value;
            
            // Simple comparison assuming format like "09:00 AM"
            if (startTime && endTime) {
                // Convert to 24-hour format for comparison
                const start24 = convertTo24Hour(startTime);
                const end24 = convertTo24Hour(endTime);
                
                if (start24 >= end24) {
                    e.preventDefault();
                    alert('End time must be after start time.');
                }
            }
        });
    }

    // Function to convert time format from "09:00 AM" to "09:00" for comparison
    function convertTo24Hour(time12h) {
        const [time, modifier] = time12h.split(' ');
        let [hours, minutes] = time.split(':');
        
        if (hours === '12') {
            hours = '00';
        }
        
        if (modifier === 'PM') {
            hours = parseInt(hours, 10) + 12;
        }
        
        return `${hours}:${minutes}`;
    }

    // Handle inventory search form
    const searchForm = document.getElementById('inventory-search-form');
    if (searchForm) {
        const categorySelect = document.getElementById('category');
        if (categorySelect) {
            categorySelect.addEventListener('change', function() {
                searchForm.submit();
            });
        }
    }

    // Registration form role selection
    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const selectedRole = this.value;
            const clientFields = document.getElementById('client-fields');
            const volunteerFields = document.getElementById('volunteer-fields');
            
            if (clientFields && volunteerFields) {
                if (selectedRole === 'client') {
                    clientFields.style.display = 'block';
                    volunteerFields.style.display = 'none';
                } else if (selectedRole === 'volunteer') {
                    clientFields.style.display = 'none';
                    volunteerFields.style.display = 'block';
                } else {
                    clientFields.style.display = 'none';
                    volunteerFields.style.display = 'none';
                }
            }
        });
    }

    // Date range form auto-submit
    const dateRangeForm = document.querySelector('form.date-range-form');
    if (dateRangeForm) {
        const submitBtn = dateRangeForm.querySelector('button[type="submit"]');
        const startDate = dateRangeForm.querySelector('#start_date');
        const endDate = dateRangeForm.querySelector('#end_date');
        
        [startDate, endDate].forEach(function(input) {
            input.addEventListener('change', function() {
                submitBtn.click();
            });
        });
    }
});
