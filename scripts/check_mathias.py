#!/usr/bin/env python3
"""
Check Mathias Fullerton's data in the database.
"""

import os
import sys

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete
from app import app

def check_mathias():
    with app.app_context():
        mathias = db.session.query(Athlete).filter_by(slug='mathias-fullerton').first()
        
        if mathias:
            print(f"✅ Found Mathias Fullerton (ID: {mathias.id})")
            print(f"\n📋 Basic Info:")
            print(f"   Full name: {mathias.full_name}")
            print(f"   Hometown: {mathias.hometown}")
            print(f"   DOB: {mathias.dob}")
            print(f"   Nationality: {mathias.nationality}")
            print(f"   World Ranking: {mathias.world_ranking}")
            
            print(f"\n🖼️  Media URLs:")
            print(f"   Card image: {mathias.card_image_url}")
            print(f"   Card back: {mathias.card_back_url}")
            print(f"   Hero image: {mathias.hero_image_url}")
            print(f"   Video: {mathias.video_url}")
            print(f"   Quote photo: {mathias.quote_photo_url}")
            print(f"   Action photo: {mathias.action_photo_url}")
            
            print(f"\n📝 Bio:")
            print(f"   Bio short: {mathias.bio_short[:50] if mathias.bio_short else None}...")
            print(f"   Bio long: {mathias.bio_long[:50] if mathias.bio_long else None}...")
            
            print(f"\n🏆 Achievements: {len(mathias.achievements)}")
            for ach in mathias.achievements:
                print(f"   - {ach.title} (order: {ach.display_order})")
            
            print(f"\n🏹 Equipment: {len(mathias.equipment)}")
            for eq in mathias.equipment:
                print(f"   - {eq.category}: {eq.brand} {eq.model or ''}")
            
            print(f"\n📊 Stats:")
            if mathias.stats:
                print(f"   Win %: {mathias.stats.win_percentage}")
                print(f"   Avg arrow: {mathias.stats.average_arrow}")
                print(f"   Tiebreak %: {mathias.stats.tiebreak_win_rate}")
            else:
                print(f"   No stats found")
            
            print(f"\n📈 Qualifications: {len(mathias.qualifications)}")
            for qual in mathias.qualifications:
                print(f"   - {qual.year}: {qual.score}")
            
            print(f"\n🔗 Socials: {mathias.socials}")
            print(f"💼 Sponsors: {len(mathias.sponsors) if mathias.sponsors else 0} sponsors")
            
        else:
            print("❌ Mathias Fullerton not found in database!")

if __name__ == '__main__':
    check_mathias()

