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

from models import db, Athlete, ArcheryDiscipline, Handedness, AthleteQualification, AthleteAchievement

def main():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        print("Set it like: DATABASE_URL=postgresql://localhost/dscards")
        return 1
    
    # Create engine
    from sqlalchemy import create_engine
    # Handle postgres:// URLs (convert to postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
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
            # Generate slug from full_name if not provided
            slug = athlete_data.get('slug')
            if not slug:
                # Generate slug from full_name (lowercase, replace spaces with hyphens)
                slug = athlete_data['full_name'].lower().replace(' ', '-').replace("'", '').replace('.', '')
            
            # Check if athlete already exists
            existing = session.query(Athlete).filter_by(slug=slug).first()
            
            if existing:
                print(f"🔄 Updating existing athlete: {athlete_data['full_name']}")
                athlete = existing
            else:
                print(f"➕ Creating new athlete: {athlete_data['full_name']}")
                athlete = Athlete()
                athlete.slug = slug
            
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
            athlete.card_back_url = athlete_data.get('card_back_url')
            athlete.hero_image_url = athlete_data.get('hero_image_url')
            athlete.video_url = athlete_data.get('video_url')
            athlete.quote_photo_url = athlete_data.get('quote_photo_url')
            athlete.action_photo_url = athlete_data.get('action_photo_url')
            
            # JSON fields - store as Python objects for JSONB
            athlete.gallery = athlete_data.get('gallery', [])
            athlete.socials = athlete_data.get('socials', {})
            athlete.sponsors = athlete_data.get('sponsors', [])
            
            if not existing:
                session.add(athlete)
            
            # Flush to get the athlete ID for qualifications
            session.flush()
            
            # Handle qualifications (time-series data)
            qualifications_data = athlete_data.get('qualifications', [])
            if qualifications_data:
                # Clear existing qualifications for updates
                if existing:
                    session.query(AthleteQualification).filter_by(athlete_id=athlete.id).delete()
                
                # Add new qualifications
                for qual_data in qualifications_data:
                    qualification = AthleteQualification(
                        athlete_id=athlete.id,
                        year=qual_data['year'],
                        score=qual_data['score']
                    )
                    session.add(qualification)
            
            # Handle achievements (relationship data)
            achievements_data = athlete_data.get('achievements', [])
            if achievements_data:
                # Clear existing achievements for updates
                if existing:
                    session.query(AthleteAchievement).filter_by(athlete_id=athlete.id).delete()
                
                # Add new achievements
                for achievement_data in achievements_data:
                    achievement = AthleteAchievement(
                        athlete_id=athlete.id,
                        title=achievement_data.get('title', ''),
                        year=achievement_data.get('year'),
                        result=achievement_data.get('result', ''),
                        medal=achievement_data.get('medal', 'none'),
                        position=achievement_data.get('position'),
                        notes=achievement_data.get('notes', ''),
                        display_order=achievement_data.get('display_order', 0)
                    )
                    session.add(achievement)
        
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
