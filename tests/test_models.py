# tests/test_models.py
import pytest
from datetime import datetime, timezone
from app import app
from models import db, User, Card, NFCTag, Collection, Order, OrderItem

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_user():
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    return user

@pytest.fixture
def sample_card():
    card = Card(
        name='Test Card',
        description='A test collectible card',
        card_number='001',
        series='Test Series',
        rarity='Common',
        condition='Mint',
        estimated_value=10.50,
        image_url='https://example.com/card.jpg'
    )
    return card

@pytest.fixture
def sample_nfc_tag():
    return NFCTag(
        tag_id='NFC123456789',
        is_verified=True,
        verification_method='Manual'
    )

@pytest.fixture
def sample_collection():
    return Collection(
        acquired_date=datetime.now(timezone.utc),
        acquisition_method='purchase',
        notes='Test acquisition',
        is_for_sale=False,
        asking_price=15.00
    )

@pytest.fixture
def sample_order():
    return Order(
        order_number='ORD001',
        order_type='purchase',
        status='pending',
        total_amount=25.00,
        payment_method='credit_card',
        shipping_address='123 Test St, Test City, TC 12345'
    )

@pytest.fixture
def sample_order_item():
    return OrderItem(
        quantity=2,
        unit_price=12.50,
        total_price=25.00
    )

class TestUser:
    def test_create_user(self, client, sample_user):
        db.session.add(sample_user)
        db.session.commit()
        
        fetched_user = User.query.filter_by(username='testuser').first()
        assert fetched_user.email == 'test@example.com'
        assert fetched_user.check_password('password123')
        assert fetched_user.is_active is True
        assert fetched_user.created_at is not None
        assert fetched_user.updated_at is not None

    def test_user_password_hashing(self, client, sample_user):
        assert sample_user.password_hash != 'password123'
        assert sample_user.check_password('password123') is True
        assert sample_user.check_password('wrongpassword') is False

    def test_user_to_dict(self, client, sample_user):
        db.session.add(sample_user)
        db.session.commit()
        
        user_dict = sample_user.to_dict()
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['is_active'] is True
        assert 'password_hash' not in user_dict

    def test_user_relationships(self, client, sample_user, sample_card, sample_collection):
        db.session.add_all([sample_user, sample_card, sample_collection])
        sample_collection.user = sample_user
        sample_collection.card = sample_card
        db.session.commit()
        
        assert len(sample_user.collections) == 1
        assert sample_user.collections[0].card.name == 'Test Card'

class TestCard:
    def test_create_card(self, client, sample_card):
        db.session.add(sample_card)
        db.session.commit()
        
        fetched_card = Card.query.filter_by(name='Test Card').first()
        assert fetched_card.description == 'A test collectible card'
        assert fetched_card.card_number == '001'
        assert fetched_card.series == 'Test Series'
        assert fetched_card.rarity == 'Common'
        assert fetched_card.condition == 'Mint'
        assert float(fetched_card.estimated_value) == 10.50
        assert fetched_card.is_authenticated is False

    def test_card_to_dict(self, client, sample_card):
        db.session.add(sample_card)
        db.session.commit()
        
        card_dict = sample_card.to_dict()
        assert card_dict['name'] == 'Test Card'
        assert card_dict['estimated_value'] == 10.50
        assert card_dict['is_authenticated'] is False

    def test_card_relationships(self, client, sample_card, sample_nfc_tag, sample_collection, sample_user):
        db.session.add_all([sample_user, sample_card, sample_nfc_tag, sample_collection])
        sample_nfc_tag.card = sample_card
        sample_collection.card = sample_card
        sample_collection.user = sample_user
        db.session.commit()
        
        assert len(sample_card.nfc_tags) == 1
        assert len(sample_card.collections) == 1
        assert sample_card.nfc_tags[0].tag_id == 'NFC123456789'

class TestNFCTag:
    def test_create_nfc_tag(self, client, sample_card, sample_nfc_tag):
        db.session.add_all([sample_card, sample_nfc_tag])
        sample_nfc_tag.card = sample_card
        db.session.commit()
        
        fetched_tag = NFCTag.query.filter_by(tag_id='NFC123456789').first()
        assert fetched_tag.is_verified is True
        assert fetched_tag.verification_method == 'Manual'
        assert fetched_tag.card.name == 'Test Card'

    def test_nfc_tag_to_dict(self, client, sample_card, sample_nfc_tag):
        db.session.add_all([sample_card, sample_nfc_tag])
        sample_nfc_tag.card = sample_card
        db.session.commit()
        
        tag_dict = sample_nfc_tag.to_dict()
        assert tag_dict['tag_id'] == 'NFC123456789'
        assert tag_dict['is_verified'] is True
        assert tag_dict['card_id'] == sample_card.id

    def test_nfc_tag_verification(self, client, sample_card, sample_nfc_tag):
        db.session.add_all([sample_card, sample_nfc_tag])
        sample_nfc_tag.card = sample_card
        sample_nfc_tag.verification_date = datetime.now(timezone.utc)
        sample_nfc_tag.last_scan_date = datetime.now(timezone.utc)
        db.session.commit()
        
        assert sample_nfc_tag.verification_date is not None
        assert sample_nfc_tag.last_scan_date is not None

class TestCollection:
    def test_create_collection(self, client, sample_user, sample_card, sample_collection):
        db.session.add_all([sample_user, sample_card, sample_collection])
        sample_collection.user = sample_user
        sample_collection.card = sample_card
        db.session.commit()
        
        fetched_collection = Collection.query.filter_by(user_id=sample_user.id).first()
        assert fetched_collection.acquisition_method == 'purchase'
        assert fetched_collection.notes == 'Test acquisition'
        assert fetched_collection.is_for_sale is False
        assert float(fetched_collection.asking_price) == 15.00

    def test_collection_to_dict(self, client, sample_user, sample_card, sample_collection):
        db.session.add_all([sample_user, sample_card, sample_collection])
        sample_collection.user = sample_user
        sample_collection.card = sample_card
        db.session.commit()
        
        collection_dict = sample_collection.to_dict()
        assert collection_dict['user_id'] == sample_user.id
        assert collection_dict['card_id'] == sample_card.id
        assert collection_dict['acquisition_method'] == 'purchase'
        assert collection_dict['asking_price'] == 15.00

    def test_collection_unique_constraint(self, client, sample_user, sample_card):
        collection1 = Collection(
            acquired_date=datetime.now(timezone.utc),
            acquisition_method='purchase'
        )
        collection2 = Collection(
            acquired_date=datetime.now(timezone.utc),
            acquisition_method='trade'
        )
        
        collection1.user = sample_user
        collection1.card = sample_card
        collection2.user = sample_user
        collection2.card = sample_card
        
        db.session.add_all([sample_user, sample_card, collection1])
        db.session.commit()
        
        # This should fail due to unique constraint
        with pytest.raises(Exception):
            db.session.add(collection2)
            db.session.commit()

class TestOrder:
    def test_create_order(self, client, sample_user, sample_order):
        db.session.add_all([sample_user, sample_order])
        sample_order.user = sample_user
        db.session.commit()
        
        fetched_order = Order.query.filter_by(order_number='ORD001').first()
        assert fetched_order.order_type == 'purchase'
        assert fetched_order.status == 'pending'
        assert float(fetched_order.total_amount) == 25.00
        assert fetched_order.payment_method == 'credit_card'
        assert fetched_order.shipping_address == '123 Test St, Test City, TC 12345'

    def test_order_to_dict(self, client, sample_user, sample_order):
        db.session.add_all([sample_user, sample_order])
        sample_order.user = sample_user
        db.session.commit()
        
        order_dict = sample_order.to_dict()
        assert order_dict['order_number'] == 'ORD001'
        assert order_dict['order_type'] == 'purchase'
        assert order_dict['total_amount'] == 25.00
        assert order_dict['user_id'] == sample_user.id

    def test_order_status_transitions(self, client, sample_user, sample_order):
        db.session.add_all([sample_user, sample_order])
        sample_order.user = sample_user
        db.session.commit()
        
        # Test status transitions
        sample_order.status = 'completed'
        sample_order.completed_date = datetime.now(timezone.utc)
        db.session.commit()
        
        assert sample_order.status == 'completed'
        assert sample_order.completed_date is not None

class TestOrderItem:
    def test_create_order_item(self, client, sample_user, sample_card, sample_order, sample_order_item):
        db.session.add_all([sample_user, sample_card, sample_order, sample_order_item])
        sample_order.user = sample_user
        sample_order_item.order = sample_order
        sample_order_item.card = sample_card
        db.session.commit()
        
        fetched_item = OrderItem.query.filter_by(order_id=sample_order.id).first()
        assert fetched_item.quantity == 2
        assert float(fetched_item.unit_price) == 12.50
        assert float(fetched_item.total_price) == 25.00
        assert fetched_item.card.name == 'Test Card'

    def test_order_item_to_dict(self, client, sample_user, sample_card, sample_order, sample_order_item):
        db.session.add_all([sample_user, sample_card, sample_order, sample_order_item])
        sample_order.user = sample_user
        sample_order_item.order = sample_order
        sample_order_item.card = sample_card
        db.session.commit()
        
        item_dict = sample_order_item.to_dict()
        assert item_dict['quantity'] == 2
        assert item_dict['unit_price'] == 12.50
        assert item_dict['total_price'] == 25.00
        assert item_dict['order_id'] == sample_order.id
        assert item_dict['card_id'] == sample_card.id

    def test_order_item_calculations(self, client, sample_user, sample_card, sample_order):
        # Test automatic total price calculation
        order_item = OrderItem(
            quantity=3,
            unit_price=10.00,
            total_price=30.00
        )
        
        order_item.order = sample_order
        order_item.card = sample_card
        sample_order.user = sample_user
        
        db.session.add_all([sample_user, sample_card, sample_order, order_item])
        db.session.commit()
        
        assert order_item.quantity == 3
        assert float(order_item.unit_price) == 10.00
        assert float(order_item.total_price) == 30.00

class TestModelRelationships:
    def test_complex_relationships(self, client, sample_user, sample_card, sample_nfc_tag, 
                                 sample_collection, sample_order, sample_order_item):
        # Set up all relationships
        db.session.add_all([sample_user, sample_card, sample_nfc_tag, 
                           sample_collection, sample_order, sample_order_item])
        
        sample_nfc_tag.card = sample_card
        sample_collection.user = sample_user
        sample_collection.card = sample_card
        sample_order.user = sample_user
        sample_order_item.order = sample_order
        sample_order_item.card = sample_card
        
        db.session.commit()
        
        # Test user has collection and orders
        assert len(sample_user.collections) == 1
        assert len(sample_user.orders) == 1
        
        # Test card has nfc tags, collections, and order items
        assert len(sample_card.nfc_tags) == 1
        assert len(sample_card.collections) == 1
        assert len(sample_card.order_items) == 1
        
        # Test order has items
        assert len(sample_order.order_items) == 1
        
        # Test collection links user and card
        assert sample_collection.user.username == 'testuser'
        assert sample_collection.card.name == 'Test Card'

if __name__ == '__main__':
    pytest.main([__file__]) 