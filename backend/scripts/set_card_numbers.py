#!/usr/bin/env python3

import os
import sys
import csv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Athlete

def set_card_numbers():
    """Set correct card numbers based on templates.csv order"""
    with app.app_context():
        print("🔍 Loading templates.csv...")
        
        # Read templates.csv to get the order
        templates_file = os.path.join(os.path.dirname(__file__), '..', 'templates.csv')
        athlete_order = []
        
        with open(templates_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                display_name = row['display_name']
                # Extract athlete name (remove " — Regular" or " - Regular" etc.)
                athlete_name = display_name.split(' — ')[0].split(' - ')[0]
                if athlete_name not in athlete_order:
                    athlete_order.append(athlete_name)
        
        print(f"📊 Found {len(athlete_order)} athletes in order:")
        for i, name in enumerate(athlete_order, 1):
            print(f"  {i}. {name}")
        
        # Update card numbers
        print(f"\n🔄 Setting card numbers...")
        for i, athlete_name in enumerate(athlete_order, 1):
            athlete = Athlete.query.filter_by(full_name=athlete_name).first()
            if athlete:
                old_number = athlete.card_number
                athlete.card_number = i
                print(f"✅ {athlete_name}: {old_number} → {i}")
            else:
                print(f"❌ Athlete {athlete_name} not found in database")
        
        # Commit changes
        db.session.commit()
        print(f"\n🎉 Successfully updated all card numbers!")

if __name__ == '__main__':
    set_card_numbers()
