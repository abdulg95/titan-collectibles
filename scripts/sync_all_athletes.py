#!/usr/bin/env python3
"""
Comprehensive script to sync all athlete data from athlete_seed.json to the database.
This includes: athlete profile, achievements, equipment, qualifications, stats, socials, and sponsors.
"""

import os
import sys
import json
import uuid
from decimal import Decimal
from datetime import datetime

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete, AthleteAchievement, AthleteEquipment, AthleteQualification, AthleteStats
from app import app

def sync_all_athletes():
    """Load all athlete data from athlete_seed.json"""
    
    # Load the seed data
    seed_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'seeds', 'athlete_seed.json')
    
    with open(seed_file, 'r') as f:
        athletes_data = json.load(f)
    
    with app.app_context():
        for athlete_data in athletes_data:
            print(f"\n{'='*60}")
            print(f"Processing: {athlete_data['full_name']}")
            print(f"{'='*60}")
            
            # Find or create athlete
            athlete = db.session.query(Athlete).filter_by(slug=athlete_data['slug']).first()
            
            if not athlete:
                athlete = Athlete(id=uuid.uuid4(), slug=athlete_data['slug'])
                db.session.add(athlete)
                print(f"✅ Created new athlete: {athlete_data['full_name']}")
            else:
                print(f"🔄 Updating existing athlete: {athlete_data['full_name']}")
            
            # Update basic fields
            athlete.full_name = athlete_data['full_name']
            athlete.sport = athlete_data.get('sport', 'Archery')
            athlete.discipline = athlete_data.get('discipline')
            athlete.nationality = athlete_data.get('nationality')
            athlete.hometown = athlete_data.get('hometown')
            athlete.handedness = athlete_data.get('handedness')
            athlete.world_ranking = athlete_data.get('world_ranking')
            athlete.best_world_ranking = athlete_data.get('best_world_ranking')
            athlete.intl_debut_year = athlete_data.get('intl_debut_year')
            
            # Parse DOB
            if athlete_data.get('dob'):
                athlete.dob = datetime.strptime(athlete_data['dob'], '%Y-%m-%d').date()
            
            # Bio and quote
            athlete.bio_short = athlete_data.get('bio_short')
            athlete.bio_long = athlete_data.get('bio_long')
            athlete.quote_text = athlete_data.get('quote_text')
            athlete.quote_source = athlete_data.get('quote_source', '')
            
            # Media URLs
            athlete.card_image_url = athlete_data.get('card_image_url')
            athlete.card_back_url = athlete_data.get('card_back_url')
            athlete.hero_image_url = athlete_data.get('hero_image_url')
            athlete.video_url = athlete_data.get('video_url')
            athlete.quote_photo_url = athlete_data.get('quote_photo_url')
            athlete.action_photo_url = athlete_data.get('action_photo_url')
            athlete.gallery = athlete_data.get('gallery', [])
            
            # Socials and sponsors (JSONB fields)
            athlete.socials = athlete_data.get('socials', {})
            athlete.sponsors = athlete_data.get('sponsors', [])
            
            db.session.flush()  # Get the athlete ID
            
            # Clear and reload achievements
            db.session.query(AthleteAchievement).filter_by(athlete_id=athlete.id).delete()
            achievements = athlete_data.get('achievements', [])
            if achievements:
                print(f"  📊 Loading {len(achievements)} achievements...")
                for ach_data in achievements:
                    if isinstance(ach_data, dict):
                        achievement = AthleteAchievement(
                            id=uuid.uuid4(),
                            athlete_id=athlete.id,
                            title=ach_data['title'],
                            result=ach_data.get('result'),
                            medal=ach_data.get('medal', 'none'),
                            notes=ach_data.get('notes'),
                            display_order=ach_data.get('display_order', 0)
                        )
                        db.session.add(achievement)
                        print(f"     ✅ {achievement.title}")
            
            # Clear and reload equipment
            db.session.query(AthleteEquipment).filter_by(athlete_id=athlete.id).delete()
            equipment = athlete_data.get('equipment', [])
            if equipment:
                print(f"  🏹 Loading {len(equipment)} equipment items...")
                for eq_data in equipment:
                    equipment_item = AthleteEquipment(
                        id=uuid.uuid4(),
                        athlete_id=athlete.id,
                        category=eq_data['category'],
                        brand=eq_data.get('brand'),
                        model=eq_data.get('model'),
                        display_order=eq_data.get('display_order', 0)
                    )
                    db.session.add(equipment_item)
                    print(f"     ✅ {equipment_item.category}: {equipment_item.brand} {equipment_item.model or ''}")
            
            # Clear and reload qualifications
            db.session.query(AthleteQualification).filter_by(athlete_id=athlete.id).delete()
            qualifications = athlete_data.get('qualifications', [])
            if qualifications:
                print(f"  📈 Loading {len(qualifications)} qualification scores...")
                for qual_data in qualifications:
                    qualification = AthleteQualification(
                        id=uuid.uuid4(),
                        athlete_id=athlete.id,
                        year=qual_data['year'],
                        score=Decimal(str(qual_data['score'])) if qual_data.get('score') else None,
                        event=qual_data.get('event')
                    )
                    db.session.add(qualification)
                    print(f"     ✅ {qualification.year}: {qualification.score}")
            
            # Create or update stats
            stats_data = athlete_data.get('stats', {})
            if stats_data and any(stats_data.get(k) for k in ['win_percentage', 'average_arrow', 'tiebreak_win_rate']):
                stats = db.session.query(AthleteStats).filter_by(athlete_id=athlete.id).first()
                
                if not stats:
                    stats = AthleteStats(id=uuid.uuid4(), athlete_id=athlete.id)
                    db.session.add(stats)
                    print(f"  📊 Creating career statistics...")
                else:
                    print(f"  🔄 Updating career statistics...")
                
                if stats_data.get('win_percentage'):
                    stats.win_percentage = Decimal(str(stats_data['win_percentage']))
                if stats_data.get('average_arrow'):
                    stats.average_arrow = Decimal(str(stats_data['average_arrow']))
                if stats_data.get('tiebreak_win_rate'):
                    stats.tiebreak_win_rate = Decimal(str(stats_data['tiebreak_win_rate']))
                stats.extras = stats_data.get('extras', {})
                
                print(f"     ✅ Win %: {stats.win_percentage}, Avg Arrow: {stats.average_arrow}, Tiebreak %: {stats.tiebreak_win_rate}")
            
            db.session.commit()
            print(f"✅ Successfully synced {athlete_data['full_name']}!")
        
        print(f"\n{'='*60}")
        print(f"🎯 All athletes synced successfully!")
        print(f"{'='*60}")

if __name__ == '__main__':
    sync_all_athletes()

