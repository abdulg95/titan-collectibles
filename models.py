from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    collections = db.relationship('Collection', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Card(db.Model):
    """Card model for collectible cards"""
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    card_number = db.Column(db.String(50), nullable=True)
    series = db.Column(db.String(100), nullable=True)
    rarity = db.Column(db.String(50), nullable=True)
    condition = db.Column(db.String(50), nullable=True)
    estimated_value = db.Column(db.Numeric(10, 2), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    is_authenticated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    nfc_tags = db.relationship('NFCTag', backref='card', lazy=True)
    collections = db.relationship('Collection', backref='card', lazy=True)
    order_items = db.relationship('OrderItem', backref='card', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'card_number': self.card_number,
            'series': self.series,
            'rarity': self.rarity,
            'condition': self.condition,
            'estimated_value': float(self.estimated_value) if self.estimated_value else None,
            'image_url': self.image_url,
            'is_authenticated': self.is_authenticated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class NFCTag(db.Model):
    """NFC Tag model for card authentication and verification"""
    __tablename__ = 'nfc_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(100), unique=True, nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime, nullable=True)
    verification_method = db.Column(db.String(100), nullable=True)
    last_scan_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag_id': self.tag_id,
            'card_id': self.card_id,
            'is_verified': self.is_verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_method': self.verification_method,
            'last_scan_date': self.last_scan_date.isoformat() if self.last_scan_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Collection(db.Model):
    """Collection model linking users to their cards"""
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    acquired_date = db.Column(db.DateTime, nullable=True)
    acquisition_method = db.Column(db.String(100), nullable=True)  # purchase, trade, gift, etc.
    notes = db.Column(db.Text, nullable=True)
    is_for_sale = db.Column(db.Boolean, default=False)
    asking_price = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Ensure unique user-card combinations
    __table_args__ = (db.UniqueConstraint('user_id', 'card_id', name='unique_user_card'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_id': self.card_id,
            'acquired_date': self.acquired_date.isoformat() if self.acquired_date else None,
            'acquisition_method': self.acquisition_method,
            'notes': self.notes,
            'is_for_sale': self.is_for_sale,
            'asking_price': float(self.asking_price) if self.asking_price else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    """Order model for tracking card purchases and sales"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_type = db.Column(db.String(20), nullable=False)  # 'purchase', 'sale'
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled, refunded
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(100), nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    tracking_number = db.Column(db.String(100), nullable=True)
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'order_type': self.order_type,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'payment_method': self.payment_method,
            'shipping_address': self.shipping_address,
            'tracking_number': self.tracking_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderItem(db.Model):
    """OrderItem model for individual items within an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'card_id': self.card_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }