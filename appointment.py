from flask import Flask, request, jsonify, abort, make_response
from uuid import uuid4
from datetime import datetime
import re
import Config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config['FLASK_APP'] = 'appoinments.py'

# Limiter to handle 5 requests per second
limiter = Limiter(get_remote_address, app= app,  
    default_limits=["5 per second"]
)


# Sample data for appointment slots (you would typically fetch this from a database)
appointment_slots = [
    {"id": 1, "date": "2023-09-15", "time": "10:00 AM", "available": True},
    {"id": 2, "date": "2023-09-15", "time": "11:00 AM", "available": True},
    {"id": 3, "date": "2023-09-14", "time": "10:00 AM", "available": True},
    {"id": 4, "date": "2023-09-13", "time": "10:00 AM", "available": True},
    {"id": 5, "date": "2023-09-12", "time": "10:00 AM", "available": True},
    {"id": 6, "date": "2023-09-11", "time": "10:00 AM", "available": True},
    {"id": 7, "date": "2023-09-10", "time": "10:00 AM", "available": True},
    {"id": 8, "date": "2023-09-09", "time": "10:00 AM", "available": True},
    {"id": 9, "date": "2023-09-08", "time": "10:00 AM", "available": True},
     {"id": 10, "date": "2023-09-07", "time": "10:00 AM", "available": True},
      {"id": 11, "date": "2023-09-06", "time": "10:00 AM", "available": True}
    # Add more slots here..
]


@app.route('/book_appointment/', methods=['POST'])
@limiter.limit("5 per second")
def book_appointment():
    """
    Book an appointment slot.

    Returns:
        dict: A dictionary with a message indicating the result of the booking.
    """
    data = request.get_json()
    date = data.get('date')
    time = data.get('time')

    # validate the inputs
    validate_date_time(date, time)

    # Iterate for available slots and book if available
    for slot in appointment_slots:
        if slot['date'] == date and slot['time'] == time:
            # Abort in case of non-availablity
            if not slot['available']:
                abort(make_response(jsonify(message="Slot is not available."), 404))

            # Return in case of success
            slot['available'] = False
            return jsonify({"message": f"Appointment booked successfully. \
                            Appointment id is {slot['id']}.", "status_code": 200})
    # Abort in case of preferred slot is not present in dataset
    abort(make_response(jsonify(message="Slot not found."), 404))


@app.route('/', methods=['GET'])
def home():
    print("Welome home")
    return jsonify(message = 'Hello')

@app.route('/check_availability', methods=['GET'])
def check_availability():
    """
    Check the availability of an appointment slot.

    Returns:
        dict: A dictionary with a message indicating the availability status.
    """

    date = request.args.get('date')
    time = request.args.get('time')

    # validate the inputs
    validate_date_time(date, time)
    
    # Iterate for an appointment slot matching the provided input
    for slot in appointment_slots:
        if slot['date'] == date and slot['time'] == time:
            # Return in case of success
            if slot['available']:
                return jsonify({'message': 'Slot is available', "status_code": 200})
            else:
                # Abort if slot is already booked
                abort(make_response(jsonify(message="Slot is not available."), 404))
    # Abort in case of preferred slot is not present in dataset
    abort(make_response(jsonify(message="Slot not found."), 404))


@app.route('/cancel_appointment/<string:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    """
    Cancel an existing appointment.

    Returns:
        dict: A dictionary with a message indicating the result of the cancellation.
    """
    # Search for an appointment slot matching the provided appointment_id
    for slot in appointment_slots:

        # Retrun in case of success
        if slot['id'] == int(appointment_id) and not slot['available']:
            slot['available'] = True
            return jsonify({"message": f"Appointment canceled successfully.", "status_code": 200})
    # Abort in case slot id is not present in dataset
    abort(make_response(jsonify(message="Slot not found."), 404))


@app.route('/list_appointments', methods=['GET'])
def list_appointments():
    """
    List all appointments.

    Returns:
        list: A list of appointments.
    """
    return jsonify(appointment_slots)

def validate_date_time(date, time):
    try:
        # Attempt to parse the input time using the specified format
        if bool(re.match(Config.TIME_FORMAT, time)):
            datetime.strptime(date, Config.DATE_FORMAT) 
        else:
            abort(make_response(jsonify(message="Invalid time format"), 400))
        return True

    except ValueError:
        # If parsing fails, the date is invalid
        abort(make_response(jsonify(message='Invalid date format'), 400))


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
