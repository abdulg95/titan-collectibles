#!/usr/bin/env python3
"""Load qualification data for Brady Ellison."""

import os
import sys
from pathlib import Path
from decimal import Decimal

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up database connection
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/dscards')

from models import db, Athlete, AthleteQualification
from app import app
import uuid

# Brady Ellison's qualification scores based on Figma graph
# The graph shows years 2015-2025 with scores ranging from 670-710
# Peak is 702 as shown in Figma
BRADY_QUALIFICATIONS = [
    {'year': 2015, 'score': Decimal('695.00'), 'event': 'World Championships'},
    {'year': 2016, 'score': Decimal('700.00'), 'event': 'Olympic Games'},
    {'year': 2017, 'score': Decimal('688.00'), 'event': 'World Championships'},
    {'year': 2018, 'score': Decimal('692.00'), 'event': 'World Championships'},
    {'year': 2019, 'score': Decimal('698.00'), 'event': 'World Championships'},
    {'year': 2020, 'score': Decimal('702.00'), 'event': 'Olympic Trials'},  # Peak as shown in Figma
    {'year': 2021, 'score': Decimal('700.00'), 'event': 'Olympic Games'},
    {'year': 2022, 'score': Decimal('695.00'), 'event': 'World Championships'},
    {'year': 2023, 'score': Decimal('698.00'), 'event': 'World Championships'},
    {'year': 2024, 'score': Decimal('700.00'), 'event': 'Olympic Games'},
    {'year': 2025, 'score': Decimal('702.00'), 'event': 'World Championships'},  # Extend to 2025
]

def load_qualifications():
    with app.app_context():
        # Find Brady Ellison
        brady = db.session.query(Athlete).filter_by(slug='brady-ellison').first()
        
        if not brady:
            print("❌ Brady Ellison not found in database")
            return
        
        print(f"✅ Found Brady Ellison (ID: {brady.id})")
        
        # Clear existing qualifications
        db.session.query(AthleteQualification).filter_by(athlete_id=brady.id).delete()
        print("🗑️  Cleared existing qualifications")
        
        # Add new qualifications
        for qual_data in BRADY_QUALIFICATIONS:
            qualification = AthleteQualification(
                id=uuid.uuid4(),
                athlete_id=brady.id,
                year=qual_data['year'],
                score=qual_data['score'],
                event=qual_data['event']
            )
            db.session.add(qualification)
            print(f"  ✅ Added: {qual_data['year']} - {qual_data['score']} ({qual_data['event']})")
        
        db.session.commit()
        print("\n🎯 Qualification data loaded successfully!")

if __name__ == '__main__':
    load_qualifications()

