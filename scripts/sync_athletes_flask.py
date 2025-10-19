#!/usr/bin/env python3
"""
Updated athlete sync script for new Titan NFC verification system.
This script syncs athletes from athlete_seed.json AND creates templates with proper template_code for new verification URLs.
Uses Flask app context for database operations.
"""

import os
import sys
import json
import re
import unicodedata

def slugify_name(name):
    """Convert name to URL-safe slug"""
    if not name:
        return ""
    # Normalize unicode characters
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    n = n.lower().strip()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n

def main():
    # Add the backend directory to Python path
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, backend_dir)
    
    try:
        from app import app
        from models import db, Athlete, CardTemplate
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print(f"Backend directory: {backend_dir}")
        print("Make sure you're running this from the backend directory")
        return 1
    
    # Read the seed data
    seed_file = os.path.join(backend_dir, 'seeds', 'athlete_seed.json')
    if not os.path.exists(seed_file):
        print(f"❌ Error: Seed file not found at {seed_file}")
        return 1
    
    with open(seed_file, 'r') as f:
        athletes_data = json.load(f)
    
    print(f"📖 Loaded {len(athletes_data)} athletes from seed file")
    
    # Template mapping for new verification system
    athlete_template_mapping = {
        'Brady Ellison': {
            'regular': '000000000001',
            'diamond': '000000000002'
        },
        'Mete Gazoz': {
            'regular': '000000000003', 
            'diamond': '000000000004'
        },
        'Ella Gibson': {
            'regular': '000000000005',
            'diamond': '000000000006'
        },
        'Deepika Kumari': {
            'regular': '000000000007',
            'diamond': '000000000008'
        },
        'Sara López': {
            'regular': '000000000009',
            'diamond': '000000000010'
        },
        'Mike Schloesser': {
            'regular': '000000000011',
            'diamond': '000000000012'
        },
        'Lim Sihyeon': {
            'regular': '000000000013',
            'diamond': '000000000014'
        },
        'Mathias Fullerton': {
            'regular': '000000000015',
            'diamond': '000000000016'
        },
        'Kim Woojin': {
            'regular': '000000000017',
            'diamond': '000000000018'
        }
    }
    
    with app.app_context():
        try:
            # Sync athletes
            for athlete_data in athletes_data:
                name = athlete_data['full_name']
                slug = slugify_name(name)
                
                # Check if athlete exists
                athlete = Athlete.query.filter_by(slug=slug).first()
                
                if athlete:
                    print(f"🔄 Syncing existing athlete: {name}")
                else:
                    print(f"➕ Creating new athlete: {name}")
                    athlete = Athlete(
                        slug=slug,
                        full_name=name,
                        sport=athlete_data.get('sport', 'Archery')
                    )
                    db.session.add(athlete)
                    db.session.flush()  # Get the ID
                
                # Update athlete with all data
                athlete.full_name = athlete_data['full_name']
                athlete.sport = athlete_data.get('sport', 'Archery')
                athlete.discipline = athlete_data.get('discipline')
                athlete.dob = athlete_data.get('dob')
                athlete.nationality = athlete_data.get('nationality')
                athlete.hometown = athlete_data.get('hometown')
                athlete.handedness = athlete_data.get('handedness')
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
                athlete.qualification_image_url = athlete_data.get('qualification_image_url')
                athlete.gallery = athlete_data.get('gallery', [])
                athlete.socials = athlete_data.get('socials', {})
                athlete.sponsors = athlete_data.get('sponsors', [])
            
            # Now create/update card templates with new verification system
            print("\n🎯 Creating/updating card templates for new verification system...")
            
            for athlete_data in athletes_data:
                name = athlete_data['full_name']
                slug = slugify_name(name)
                
                # Get athlete
                athlete = Athlete.query.filter_by(slug=slug).first()
                if not athlete:
                    print(f"⚠️  Skipping templates for {name} - athlete not found")
                    continue
                
                # Create templates for both regular and diamond versions
                for version in ['regular', 'diamond']:
                    template_code = athlete_template_mapping.get(name, {}).get(version)
                    
                    if not template_code:
                        print(f"⚠️  No template code found for {name} {version}")
                        continue
                    
                    # Check if template already exists
                    existing_template = CardTemplate.query.filter_by(
                        athlete_id=athlete.id, 
                        version=version
                    ).first()
                    
                    if existing_template:
                        # Update existing template with new template_code
                        existing_template.template_code = template_code
                        print(f"🔄 Updated {name} {version} template with code {template_code}")
                    else:
                        # Create new template
                        template = CardTemplate(
                            athlete_id=athlete.id,
                            version=version,
                            template_code=template_code,
                            minted_count=0
                        )
                        db.session.add(template)
                        print(f"➕ Created {name} {version} template with code {template_code}")
            
            # Commit all changes
            db.session.commit()
            print(f"\n✅ Successfully synced {len(athletes_data)} athletes and their templates")
            print("🔗 New verification URLs format: https://titansportshq.com/scan?t=000000000002")
            
            return 0
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error syncing athletes: {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    sys.exit(main())
