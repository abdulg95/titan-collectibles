from flask import Flask, request, jsonify
from models import db

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///titan_collectibles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.json
    # Validate data, create user in DB
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/cards/<int:card_id>', methods=['GET'])
def get_card_details(card_id):
    # Fetch card from DB
    card = {}  # mock data
    return jsonify(card)

@app.route('/api/collections', methods=['POST'])
def add_to_collection():
    data = request.json
    # Link card to user in DB
    return jsonify({"message": "Card added to collection"})

@app.route('/api/nfc/verify', methods=['POST'])
def verify_nfc():
    data = request.json
    # Call external API + logic
    result = {"success": True, "card": {"id": 1, "name": "Sample Card"}}
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
