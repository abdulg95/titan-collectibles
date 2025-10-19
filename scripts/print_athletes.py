#!/usr/bin/env python3
"""
Print all athletes and their data from the database
"""

import os
import sys
from sqlalchemy import create_engine, text
import json

# Add the parent directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete

def main():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Set it like: DATABASE_URL=postgresql://localhost/dscards")
        return 1
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create a session
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query all athletes
        athletes = session.query(Athlete).all()
        
        if not athletes:
            print("📭 No athletes found in database")
            return 0
        
        print(f"🏹 Found {len(athletes)} athletes:\n")
        
        for i, athlete in enumerate(athletes, 1):
            print(f"--- Athlete {i}: {athlete.full_name} ---")
            print(f"ID: {athlete.id}")
            print(f"Slug: {athlete.slug}")
            print(f"Sport: {athlete.sport}")
            print(f"Discipline: {athlete.discipline}")
            print(f"DOB: {athlete.dob}")
            print(f"Nationality: {athlete.nationality}")
            print(f"Hometown: {athlete.hometown}")
            print(f"Handedness: {athlete.handedness}")
            print(f"World Ranking: {athlete.world_ranking}")
            print(f"Best World Ranking: {athlete.best_world_ranking}")
            print(f"International Debut Year: {athlete.intl_debut_year}")
            print(f"Bio Short: {athlete.bio_short[:100] if athlete.bio_short else 'None'}...")
            print(f"Quote: {athlete.quote_text}")
            print(f"Card Image URL: {athlete.card_image_url}")
            print(f"Hero Image URL: {athlete.hero_image_url}")
            print(f"Video URL: {athlete.video_url}")
            
            if athlete.socials:
                print(f"Socials: {json.dumps(athlete.socials, indent=2)}")
            
            if athlete.sponsors:
                print(f"Sponsors: {json.dumps(athlete.sponsors, indent=2)}")
            
            if athlete.achievements:
                print(f"Achievements: {json.dumps(athlete.achievements, indent=2)}")
            
            print(f"Created: {athlete.created_at}")
            print(f"Updated: {athlete.updated_at}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error querying database: {e}")
        return 1
    finally:
        session.close()

if __name__ == "__main__":
    sys.exit(main())
