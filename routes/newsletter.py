from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError
from app import db
from models import Newsletter

newsletter_bp = Blueprint('newsletter', __name__)

@newsletter_bp.route('/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    """
    Subscribe an email to the newsletter
    Expected JSON: {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if email already exists
        existing_subscription = Newsletter.query.filter_by(email=email).first()
        if existing_subscription:
            if existing_subscription.is_active:
                return jsonify({'message': 'Email is already subscribed to the newsletter'}), 200
            else:
                # Reactivate subscription
                existing_subscription.is_active = True
                db.session.commit()
                return jsonify({'message': 'Newsletter subscription reactivated successfully'}), 200
        
        # Create new subscription
        newsletter_subscription = Newsletter(email=email)
        db.session.add(newsletter_subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully subscribed to newsletter',
            'subscription': newsletter_subscription.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@newsletter_bp.route('/newsletter/unsubscribe', methods=['POST'])
def unsubscribe_newsletter():
    """
    Unsubscribe an email from the newsletter
    Expected JSON: {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        # Find subscription
        subscription = Newsletter.query.filter_by(email=email).first()
        if not subscription:
            return jsonify({'error': 'Email not found in newsletter subscriptions'}), 404
        
        if not subscription.is_active:
            return jsonify({'message': 'Email is already unsubscribed'}), 200
        
        # Deactivate subscription (soft delete)
        subscription.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Successfully unsubscribed from newsletter'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@newsletter_bp.route('/newsletter/subscribers', methods=['GET'])
def get_subscribers():
    """
    Get all active newsletter subscribers (admin endpoint)
    """
    try:
        subscribers = Newsletter.query.filter_by(is_active=True).all()
        
        return jsonify({
            'total_subscribers': len(subscribers),
            'subscribers': [sub.to_dict() for sub in subscribers]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@newsletter_bp.route('/newsletter/check/<email>', methods=['GET'])
def check_subscription_status(email):
    """
    Check if an email is subscribed to the newsletter
    """
    try:
        email = email.strip().lower()
        
        subscription = Newsletter.query.filter_by(email=email).first()
        
        if subscription and subscription.is_active:
            return jsonify({
                'subscribed': True,
                'subscription': subscription.to_dict()
            }), 200
        else:
            return jsonify({'subscribed': False}), 200
            
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500 