// Chart utilities for Food Pantry Management System

/**
 * Create a bar chart to display inventory by category
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - The data for the chart
 */
function createInventoryChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Prepare data for chart
    const categories = Object.keys(data);
    const quantities = categories.map(category => data[category].quantity);
    const itemCounts = categories.map(category => data[category].count);
    
    // Create a stacked bar chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Total Quantity',
                    data: quantities,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantity'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Category'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        footer: function(tooltipItems) {
                            const index = tooltipItems[0].dataIndex;
                            return `Number of items: ${itemCounts[index]}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create a pie chart to display request status distribution
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - The data for the chart
 */
function createRequestStatusChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Prepare data for chart
    const statuses = Object.keys(data);
    const counts = statuses.map(status => data[status]);
    
    // Define colors for different statuses
    const colors = {
        'Pending': 'rgba(255, 193, 7, 0.6)',
        'Approved': 'rgba(23, 162, 184, 0.6)',
        'In Progress': 'rgba(0, 123, 255, 0.6)',
        'Completed': 'rgba(40, 167, 69, 0.6)',
        'Cancelled': 'rgba(220, 53, 69, 0.6)'
    };
    
    // Map status to colors
    const backgroundColor = statuses.map(status => colors[status] || 'rgba(108, 117, 125, 0.6)');
    
    // Create a pie chart
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: statuses,
            datasets: [{
                data: counts,
                backgroundColor: backgroundColor,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

/**
 * Create a bar chart for volunteer hours
 * @param {string} canvasId - The ID of the canvas element
 * @param {Object} data - The data for the chart
 */
function createVolunteerHoursChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Prepare data for chart
    const volunteers = Object.keys(data);
    const hours = volunteers.map(volunteer => data[volunteer].toFixed(2));
    
    // Create a horizontal bar chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: volunteers,
            datasets: [{
                label: 'Hours',
                data: hours,
                backgroundColor: 'rgba(0, 123, 255, 0.6)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    }
                }
            }
        }
    });
}

/**
 * Create a line chart for daily requests over time
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} requests - Array of request objects with dates
 * @param {Date} startDate - Start date for the chart
 * @param {Date} endDate - End date for the chart
 */
function createRequestTrendChart(canvasId, requests, startDate, endDate) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create date range array
    const dateRange = [];
    const currentDate = new Date(startDate);
    while (currentDate <= endDate) {
        dateRange.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    // Count requests per day
    const requestCounts = {};
    dateRange.forEach(date => {
        const dateString = date.toISOString().split('T')[0];
        requestCounts[dateString] = 0;
    });
    
    requests.forEach(request => {
        const date = new Date(request.created_at);
        const dateString = date.toISOString().split('T')[0];
        if (requestCounts[dateString] !== undefined) {
            requestCounts[dateString]++;
        }
    });
    
    // Format dates for display
    const formattedDates = dateRange.map(date => {
        return `${date.getMonth() + 1}/${date.getDate()}`;
    });
    
    // Get request counts in order
    const counts = dateRange.map(date => {
        const dateString = date.toISOString().split('T')[0];
        return requestCounts[dateString];
    });
    
    // Create line chart
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [{
                label: 'Daily Requests',
                data: counts,
                fill: false,
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    },
                    title: {
                        display: true,
                        text: 'Number of Requests'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}
