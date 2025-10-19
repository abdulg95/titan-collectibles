#!/usr/bin/env python3
"""
Load athlete data from the seed JSON file
"""

import os
import sys
import json
from datetime import date

# Add the parent directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete, ArcheryDiscipline, Handedness

def main():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Set it like: DATABASE_URL=postgresql://localhost/dscards")
        return 1
    
    # Create engine
    from sqlalchemy import create_engine
    engine = create_engine(database_url)
    
    # Create tables
    db.metadata.create_all(engine)
    
    # Create a session
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Read the seed data
        seed_file = os.path.join(os.path.dirname(__file__), '..', 'seeds', 'athlete_seed.json')
        if not os.path.exists(seed_file):
            print(f"❌ Error: Seed file not found at {seed_file}")
            return 1
        
        with open(seed_file, 'r') as f:
            athletes_data = json.load(f)
        
        print(f"📖 Loaded {len(athletes_data)} athletes from seed file")
        
        # Process each athlete
        for athlete_data in athletes_data:
            # Check if athlete already exists
            existing = session.query(Athlete).filter_by(slug=athlete_data['slug']).first()
            
            if existing:
                print(f"🔄 Updating existing athlete: {athlete_data['full_name']}")
                athlete = existing
            else:
                print(f"➕ Creating new athlete: {athlete_data['full_name']}")
                athlete = Athlete()
                athlete.slug = athlete_data['slug']
            
            # Update athlete data
            athlete.full_name = athlete_data['full_name']
            athlete.sport = athlete_data.get('sport', 'Archery')
            
            # Handle discipline enum
            if athlete_data.get('discipline'):
                try:
                    athlete.discipline = athlete_data['discipline']
                except:
                    pass
            
            # Handle handedness enum
            if athlete_data.get('handedness'):
                try:
                    athlete.handedness = athlete_data['handedness']
                except:
                    pass
            
            # Handle date fields
            if athlete_data.get('dob'):
                athlete.dob = date.fromisoformat(athlete_data['dob'])
            
            # Simple fields
            athlete.nationality = athlete_data.get('nationality')
            athlete.hometown = athlete_data.get('hometown')
            athlete.world_ranking = athlete_data.get('world_ranking')
            athlete.best_world_ranking = athlete_data.get('best_world_ranking')
            athlete.intl_debut_year = athlete_data.get('intl_debut_year')
            athlete.bio_short = athlete_data.get('bio_short')
            athlete.bio_long = athlete_data.get('bio_long')
            athlete.quote_text = athlete_data.get('quote_text')
            athlete.quote_source = athlete_data.get('quote_source')
            athlete.card_image_url = athlete_data.get('card_image_url')
            athlete.hero_image_url = athlete_data.get('hero_image_url')
            athlete.video_url = athlete_data.get('video_url')
            
            # JSON fields - store as Python objects for JSONB
            athlete.gallery = athlete_data.get('gallery', [])
            athlete.socials = athlete_data.get('socials', {})
            athlete.sponsors = athlete_data.get('sponsors', [])
            athlete.achievements = athlete_data.get('achievements', [])
            
            if not existing:
                session.add(athlete)
        
        # Commit all changes
        session.commit()
        print(f"✅ Successfully loaded {len(athletes_data)} athletes")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error loading athletes: {e}")
        session.rollback()
        return 1
    finally:
        session.close()

if __name__ == "__main__":
    sys.exit(main())
