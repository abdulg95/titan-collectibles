#!/usr/bin/env python3
"""Load equipment data for Brady Ellison."""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up database connection
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/dscards')

from models import db, Athlete, AthleteEquipment
from app import app
import uuid

# Brady Ellison's equipment based on Figma design
BRADY_EQUIPMENT = [
    {'category': 'Riser', 'brand': 'Hoyt', 'model': 'Formula XD', 'display_order': 0},
    {'category': 'Limbs', 'brand': 'Hoyt', 'model': 'Axia', 'display_order': 1},
    {'category': 'Stabilizers', 'brand': 'Shrewd', 'model': None, 'display_order': 2},
    {'category': 'Sight', 'brand': 'Axcel', 'model': 'Achieve XP Pro', 'display_order': 3},
    {'category': 'Pin', 'brand': 'Shrewd', 'model': None, 'display_order': 4},
    {'category': 'Plunger', 'brand': 'Beiter', 'model': None, 'display_order': 5},
    {'category': 'Rest', 'brand': 'Shibuya', 'model': 'Ultima', 'display_order': 6},
    {'category': 'Arrow', 'brand': 'Easton', 'model': 'X10', 'display_order': 7},
    {'category': 'Vane', 'brand': 'Spider', 'model': 'Vanes', 'display_order': 8},
    {'category': 'Nock', 'brand': 'Beiter', 'model': None, 'display_order': 9},
    {'category': 'Tab', 'brand': 'Axcel', 'model': 'Contour', 'display_order': 10},
]

def load_equipment():
    with app.app_context():
        # Find Brady Ellison
        brady = db.session.query(Athlete).filter_by(slug='brady-ellison').first()
        
        if not brady:
            print("❌ Brady Ellison not found in database")
            return
        
        print(f"✅ Found Brady Ellison (ID: {brady.id})")
        
        # Clear existing equipment
        db.session.query(AthleteEquipment).filter_by(athlete_id=brady.id).delete()
        print("🗑️  Cleared existing equipment")
        
        # Add new equipment
        for eq_data in BRADY_EQUIPMENT:
            equipment = AthleteEquipment(
                id=uuid.uuid4(),
                athlete_id=brady.id,
                category=eq_data['category'],
                brand=eq_data['brand'],
                model=eq_data['model'],
                display_order=eq_data['display_order']
            )
            db.session.add(equipment)
            
            display_name = f"{eq_data['brand']} {eq_data['model']}" if eq_data['model'] else eq_data['brand']
            print(f"  ✅ Added: {display_name} ({eq_data['category']})")
        
        db.session.commit()
        print("\n🎯 Equipment data loaded successfully!")

if __name__ == '__main__':
    load_equipment()

