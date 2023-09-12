import json
import pytest
import os
import sys
import time

# Importing the Flask app from project
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from appointment import app

# Create a test client fixture
@pytest.fixture
def client():
    """
    Create a test client for the Flask app.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test booking an appointment
def test_book_appointment(client):
    """
    Test booking an appointment.
    """
    appointment_data = {
        "date": "2023-09-08",
        "time": "10:00 AM"
    }

    response = client.post('/book_appointment/', json=appointment_data)
    
    assert response.status_code == 200
    assert b"Appointment booked successfully" in response.data

# Test booking appointments with rate limiting
def test_book_appointment_rate_limit(client):
    appointment_data = [{
            "date": "2023-09-15",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-14",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-13",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-12",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-11",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-10",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-09",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-07",
            "time": "10:00 AM"
        },
        {
            "date": "2023-09-06",
            "time": "10:00 AM"
        },
    ]
    for i in range(5):
        response = client.post('/book_appointment/', json=appointment_data[i])
    response = client.post('/book_appointment/', json=appointment_data[i+1])
    assert response.status_code == 429

    # Wait for a moment (outside the rate limit window)
    time.sleep(1)
    
    # After waiting, the request should be allowed again
    response = client.post('/book_appointment/', json=appointment_data[i+2])
    assert response.status_code == 200

# Test booking an appointment again (when the slot is not available)
def test_book_appointment_again(client):
    """
    Test booking an appointment again (when the slot is not available)
    """
    appointment_data = {
        "date": "2023-09-15",
        "time": "10:00 AM"
    }

    response = client.post('/book_appointment/', json=appointment_data)
    
    assert response.status_code == 404
    assert b"Slot is not available." in response.data

# Test booking an appointment with an invalid slot.
def test_book_appointment_invalid_slot(client):
    """
    Test booking an appointment with an invalid slot.
    """

    appointment_data = {
        "date": "2023-09-01",
        "time": "10:00 AM"
    }

    response = client.post('/book_appointment/', json=appointment_data)
    
    assert response.status_code == 404
    assert b"Slot not found." in response.data
# Test checking appointment availability
def test_check_availability(client):
    """
    Test checking appointment availability.
    """

    appointment_data = {
        "date": "2023-09-15",
        "time": "11:00 AM"
    }

    response = client.get('/check_availability', query_string=appointment_data)

    assert response.status_code == 200
    assert b"Slot is available" in response.data

# Test canceling an appointment
def test_cancel_appointment(client):
    """
    Test canceling an appointment.
    """

    appointment_id = "1"

    response = client.post(f'/cancel_appointment/{appointment_id}')

    assert response.status_code == 200
    assert b"Appointment canceled successfully" in response.data

# Test canceling an invalid appointment
def test_cancel_appointment_invalid(client):
    """
    Test canceling an appointment.
    """
    appointment_id = "1"

    response = client.post(f'/cancel_appointment/{appointment_id}')

    assert response.status_code == 404
    assert b"Slot not found." in response.data

# Test listing all appointments
def test_list_appointments(client):
    """
    Test listing all appointments.
    """
    response = client.get('/list_appointments')
    
    assert response.status_code == 200
    appointments = json.loads(response.data)
    assert isinstance(appointments, list)
    for appointment in appointments:
        assert "id" in appointment
        assert "date" in appointment
        assert "time" in appointment
        assert "available" in appointment

# Run tests if the script is executed directly
if __name__ == '__main__':
    pytest.main()
