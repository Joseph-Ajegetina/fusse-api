from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Customer(db.Model):
    __tablename__ = 'customer'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='customer', lazy=True)
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Table(db.Model):
    __tablename__ = 'table'
    
    table_id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False, unique=True)
    capacity = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='table', lazy=True)
    
    def to_dict(self):
        return {
            'table_id': self.table_id,
            'table_number': self.table_number,
            'capacity': self.capacity,
            'is_active': self.is_active
        }

class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('table.table_id'), nullable=False)
    reservation_datetime = db.Column(db.DateTime, nullable=False)
    num_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='confirmed', nullable=False)  # confirmed, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'customer_id': self.customer_id,
            'table_id': self.table_id,
            'table_number': self.table.table_number if self.table else None,
            'reservation_datetime': self.reservation_datetime.isoformat() if self.reservation_datetime else None,
            'num_of_guests': self.num_of_guests,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'customer_name': self.customer.name if self.customer else None,
            'customer_email': self.customer.email if self.customer else None
        }

class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    
    newsletter_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    date_subscribed = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        return {
            'newsletter_id': self.newsletter_id,
            'email': self.email,
            'date_subscribed': self.date_subscribed.isoformat() if self.date_subscribed else None,
            'is_active': self.is_active
        }

class MenuCategory(db.Model):
    __tablename__ = 'menu_category'
    
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    menu_items = db.relationship('MenuItem', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'items': [item.to_dict() for item in self.menu_items if item.is_available]
        }

class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    
    item_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('menu_category.category_id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)  # URL or path to menu item image
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'item_id': self.item_id,
            'category_id': self.category_id,
            'item_name': self.item_name,
            'description': self.description,
            'price': float(self.price) if self.price else 0,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'display_order': self.display_order
        }

class Admin(db.Model):
    __tablename__ = 'admin'
    
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # Should be hashed
    email = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    def to_dict(self):
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        } 