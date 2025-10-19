#!/usr/bin/env python3
"""Load career statistics for Brady Ellison."""

import os
import sys
from pathlib import Path
from decimal import Decimal

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Set up database connection
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/dscards')

from models import db, Athlete, AthleteStats
from app import app
import uuid

# Brady Ellison's career statistics based on Figma design
BRADY_STATS = {
    'win_percentage': Decimal('75.00'),      # 75% (214-73)
    'average_arrow': Decimal('9.39'),       # 9.39 out of 10
    'tiebreak_win_rate': Decimal('66.00'),  # 66% (31-16)
}

def load_stats():
    with app.app_context():
        # Find Brady Ellison
        brady = db.session.query(Athlete).filter_by(slug='brady-ellison').first()
        
        if not brady:
            print("❌ Brady Ellison not found in database")
            return
        
        print(f"✅ Found Brady Ellison (ID: {brady.id})")
        
        # Check if stats already exist
        existing_stats = db.session.query(AthleteStats).filter_by(athlete_id=brady.id).first()
        
        if existing_stats:
            # Update existing stats
            existing_stats.win_percentage = BRADY_STATS['win_percentage']
            existing_stats.average_arrow = BRADY_STATS['average_arrow']
            existing_stats.tiebreak_win_rate = BRADY_STATS['tiebreak_win_rate']
            print("📊 Updated existing career statistics")
        else:
            # Create new stats
            stats = AthleteStats(
                id=uuid.uuid4(),
                athlete_id=brady.id,
                win_percentage=BRADY_STATS['win_percentage'],
                average_arrow=BRADY_STATS['average_arrow'],
                tiebreak_win_rate=BRADY_STATS['tiebreak_win_rate']
            )
            db.session.add(stats)
            print("📊 Created new career statistics")
        
        print(f"  ✅ Win Percentage: {BRADY_STATS['win_percentage']}%")
        print(f"  ✅ Average Arrow: {BRADY_STATS['average_arrow']}")
        print(f"  ✅ Tiebreak Win Rate: {BRADY_STATS['tiebreak_win_rate']}%")
        
        db.session.commit()
        print("\n🎯 Career statistics loaded successfully!")

if __name__ == '__main__':
    load_stats()

