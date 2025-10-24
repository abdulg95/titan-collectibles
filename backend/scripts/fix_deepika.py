#!/usr/bin/env python3
"""
Fix Deepika Kumari's data in the production database.
"""

import os
import sys
import json
from datetime import date

# Add the parent directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete, ArcheryDiscipline, Handedness, AthleteQualification, AthleteAchievement, Medal

def main():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        return 1
    
    # Handle postgres:// URLs (convert to postgresql://)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
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
        # Find Deepika
        deepika = session.query(Athlete).filter(Athlete.full_name.ilike('%deepika%')).first()
        if not deepika:
            print("❌ Deepika not found")
            return 1
        
        print(f"🔍 Found Deepika: {deepika.full_name}")
        print(f"   Current slug: {deepika.slug}")
        print(f"   Current socials: {deepika.socials}")
        print(f"   Current sponsors: {len(deepika.sponsors) if deepika.sponsors else 0}")
        print(f"   Current achievements: {len(deepika.achievements)}")
        
        # Fix slug
        slug = deepika.full_name.lower().replace(' ', '-').replace("'", '').replace('.', '')
        deepika.slug = slug
        print(f"✅ Fixed slug: {slug}")
        
        # Fix socials
        deepika.socials = {
            "x": "",
            "tiktok": "",
            "youtube": "",
            "facebook": "https://www.facebook.com/DeepikaArchery/",
            "instagram": "https://www.instagram.com/dkumari.archer/?hl=en"
        }
        print(f"✅ Fixed socials: {deepika.socials}")
        
        # Fix sponsors
        deepika.sponsors = [
            {
                "url": "https://ramrods.com",
                "name": "Ramrods",
                "logo_url": "/assets/sponsors/ramrods.png"
            },
            {
                "url": "https://beiter.com",
                "name": "Beiter",
                "logo_url": "/assets/sponsors/beiter.png"
            },
            {
                "url": "https://shibuya-archery.com",
                "name": "Shibuya",
                "logo_url": "/assets/sponsors/shibuya.png"
            },
            {
                "url": "https://eastonarchery.com",
                "name": "Easton",
                "logo_url": "/assets/sponsors/easton.png"
            },
            {
                "url": "https://hoyt.com",
                "name": "Hoyt",
                "logo_url": "/assets/sponsors/hoyt.png"
            }
        ]
        print(f"✅ Fixed sponsors: {len(deepika.sponsors)} sponsors")
        
        # Clear existing achievements and add new ones
        session.query(AthleteAchievement).filter_by(athlete_id=deepika.id).delete()
        
        achievements_data = [
            {
                "title": "Olympics",
                "result": "4x Olympian",
                "year": None,
                "notes": "silver",
                "display_order": 0
            },
            {
                "title": "World Archery Championships",
                "result": "Multi-time medallist",
                "year": None,
                "notes": "gold,gold,silver,silver,bronze",
                "display_order": 1
            },
            {
                "title": "World Cup Final",
                "result": "Multi-time medallist",
                "year": None,
                "notes": "silver,silver,silver,silver,silver",
                "display_order": 2
            },
            {
                "title": "World Cup Stages",
                "result": "Multi-time medallist",
                "year": None,
                "notes": "gold,gold,gold,gold,gold",
                "display_order": 3
            },
            {
                "title": "Historic World No. 1 Ranking",
                "result": "First Indian archer",
                "year": None,
                "notes": "silver",
                "display_order": 4
            }
        ]
        
        for achievement_data in achievements_data:
            achievement = AthleteAchievement(
                athlete_id=deepika.id,
                title=achievement_data.get('title', ''),
                year=achievement_data.get('year'),
                result=achievement_data.get('result', ''),
                medal=achievement_data.get('medal', 'none'),
                position=achievement_data.get('position'),
                notes=achievement_data.get('notes', ''),
                display_order=achievement_data.get('display_order', 0)
            )
            session.add(achievement)
        
        print(f"✅ Fixed achievements: {len(achievements_data)} achievements")
        
        # Commit all changes
        session.commit()
        print(f"🎉 Successfully fixed Deepika's data!")
        
        # Verify the fix
        session.refresh(deepika)
        print(f"\n📊 Verification:")
        print(f"   Slug: {deepika.slug}")
        print(f"   Socials: {deepika.socials}")
        print(f"   Sponsors: {len(deepika.sponsors)}")
        print(f"   Achievements: {len(deepika.achievements)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error fixing Deepika: {e}")
        session.rollback()
        return 1
    finally:
        session.close()

if __name__ == "__main__":
    sys.exit(main())
