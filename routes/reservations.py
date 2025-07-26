from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app import db
from models import Reservation, Customer, Table
import random

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations', methods=['POST'])
def create_reservation():
    """
    Create a new reservation
    Expected JSON: {
        "customer_name": "John Doe",
        "email": "john@example.com", 
        "phone_number": "123-456-7890",
        "reservation_datetime": "2024-01-15T19:00:00",
        "num_of_guests": 4
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['customer_name', 'email', 'reservation_datetime', 'num_of_guests']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse reservation datetime
        try:
            reservation_datetime = datetime.fromisoformat(data['reservation_datetime'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
        # Validate reservation is in the future
        if reservation_datetime <= datetime.utcnow():
            return jsonify({'error': 'Reservation must be in the future'}), 400
        
        # Validate number of guests
        num_guests = int(data['num_of_guests'])
        if num_guests < 1 or num_guests > 12:  # Assuming max table capacity is 12
            return jsonify({'error': 'Number of guests must be between 1 and 12'}), 400
        
        # Check table availability
        available_table = find_available_table(reservation_datetime, num_guests)
        if not available_table:
            return jsonify({'error': 'No tables available for the selected time slot'}), 409
        
        # Create or get customer
        customer = Customer.query.filter_by(email=data['email']).first()
        if not customer:
            customer = Customer(
                name=data['customer_name'],
                email=data['email'],
                phone_number=data.get('phone_number')
            )
            db.session.add(customer)
            db.session.flush()  # Get customer_id without committing
        
        # Create reservation
        reservation = Reservation(
            customer_id=customer.customer_id,
            table_id=available_table.table_id,
            reservation_datetime=reservation_datetime,
            num_of_guests=num_guests,
            status='confirmed'
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation created successfully',
            'reservation': reservation.to_dict(),
            'table_number': available_table.table_number
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@reservations_bp.route('/reservations/check-availability', methods=['POST'])
def check_availability():
    """
    Check table availability for a specific datetime and party size
    Expected JSON: {
        "reservation_datetime": "2024-01-15T19:00:00",
        "num_of_guests": 4
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'reservation_datetime' not in data or 'num_of_guests' not in data:
            return jsonify({'error': 'Missing required fields: reservation_datetime, num_of_guests'}), 400
        
        # Parse datetime
        try:
            reservation_datetime = datetime.fromisoformat(data['reservation_datetime'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid datetime format'}), 400
        
        num_guests = int(data['num_of_guests'])
        
        # Find available table
        available_table = find_available_table(reservation_datetime, num_guests)
        
        if available_table:
            return jsonify({
                'available': True,
                'table_number': available_table.table_number,
                'capacity': available_table.capacity
            }), 200
        else:
            return jsonify({'available': False}), 200
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@reservations_bp.route('/reservations/slots/available', methods=['GET'])
def get_available_time_slots():
    """
    Get available time slots for a specific date and party size
    Query parameters:
    - date: YYYY-MM-DD format (required)
    - num_of_guests: integer (required)
    
    Example: /api/reservations/available-slots?date=2024-01-15&num_of_guests=4
    """
    try:
        # Get query parameters
        date_str = request.args.get('date')
        num_guests_str = request.args.get('num_of_guests')
        
        if not date_str or not num_guests_str:
            return jsonify({'error': 'Missing required query parameters: date, num_of_guests'}), 400
        
        # Parse date
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate date is not in the past
        if date_obj < datetime.now().date():
            return jsonify({'error': 'Date cannot be in the past'}), 400
        
        try:
            num_guests = int(num_guests_str)
        except ValueError:
            return jsonify({'error': 'num_of_guests must be a valid integer'}), 400
        
        if num_guests < 1 or num_guests > 12:
            return jsonify({'error': 'Number of guests must be between 1 and 12'}), 400
        
        # Get restaurant operating hours based on SRS requirements
        # Monday-Saturday: 5:00PM - 11:00 PM; Sunday: 5:00 PM - 9:00 PM
        day_of_week = date_obj.weekday()  # 0=Monday, 6=Sunday
        
        if day_of_week == 6:  # Sunday
            start_hour = 17  # 5:00 PM
            end_hour = 21    # 9:00 PM
        else:  # Monday-Saturday
            start_hour = 17  # 5:00 PM
            end_hour = 23    # 11:00 PM
        
        # Generate 30-minute time slots
        available_slots = []
        slot_duration_minutes = 30
        
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                # Skip the last slot if it would go past closing time
                slot_time = datetime.combine(date_obj, datetime.min.time().replace(hour=hour, minute=minute))
                slot_end_time = slot_time + timedelta(hours=2)  # 2-hour reservation duration
                
                if slot_end_time.hour > end_hour:
                    continue
                
                # Check if this time slot is available
                available_table = find_available_table(slot_time, num_guests)
                
                if available_table:
                    available_slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'datetime': slot_time.isoformat(),
                        'available_table_count': count_available_tables(slot_time, num_guests)
                    })
        
        return jsonify({
            'date': date_str,
            'num_of_guests': num_guests,
            'available_slots': available_slots,
            'total_available_slots': len(available_slots)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    """Get reservation details by ID"""
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        return jsonify(reservation.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation_status(reservation_id):
    """
    Update reservation status (cancel, confirm, complete)
    Expected JSON: {"status": "cancelled"}
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Missing required field: status'}), 400
        
        valid_statuses = ['confirmed', 'cancelled', 'completed']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        reservation.status = data['status']
        db.session.commit()
        
        return jsonify({
            'message': 'Reservation status updated successfully',
            'reservation': reservation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

def find_available_table(reservation_datetime, num_guests):
    """
    Find an available table for the given datetime and party size
    Returns a random table from available tables that can accommodate the party
    """
    available_tables = get_available_tables(reservation_datetime, num_guests)
    
    if not available_tables:
        return None
    
    # Return a random available table (as per requirements)
    return random.choice(available_tables)

def count_available_tables(reservation_datetime, num_guests):
    """
    Count the number of available tables for the given datetime and party size
    """
    available_tables = get_available_tables(reservation_datetime, num_guests)
    return len(available_tables)

def get_available_tables(reservation_datetime, num_guests):
    """
    Get all available tables for the given datetime and party size
    Returns a list of available table objects
    """
    # Define time slot duration (assuming 2 hours per reservation)
    slot_duration = timedelta(hours=2)
    slot_start = reservation_datetime
    slot_end = reservation_datetime + slot_duration
    
    # Find tables that can accommodate the party size
    suitable_tables = Table.query.filter(
        and_(
            Table.capacity >= num_guests,
            Table.is_active == True
        )
    ).all()
    
    if not suitable_tables:
        return []
    
    # Check which tables are available during the requested time slot
    available_tables = []
    for table in suitable_tables:
        # Check for conflicting reservations
        conflicting_reservations = Reservation.query.filter(
            and_(
                Reservation.table_id == table.table_id,
                Reservation.status == 'confirmed',
                or_(
                    # Reservation starts during our slot
                    and_(
                        Reservation.reservation_datetime >= slot_start,
                        Reservation.reservation_datetime < slot_end
                    ),
                    # Reservation ends during our slot
                    and_(
                        Reservation.reservation_datetime + slot_duration > slot_start,
                        Reservation.reservation_datetime + slot_duration <= slot_end
                    ),
                    # Reservation encompasses our slot
                    and_(
                        Reservation.reservation_datetime <= slot_start,
                        Reservation.reservation_datetime + slot_duration >= slot_end
                    )
                )
            )
        ).count()
        
        if conflicting_reservations == 0:
            available_tables.append(table)
    
    return available_tables 