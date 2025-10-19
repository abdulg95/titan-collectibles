#!/usr/bin/env python3
"""
Updated athlete sync script for new Titan NFC verification system.
This script syncs athletes from athlete_seed.json AND creates templates with proper template_code for new verification URLs.
"""

import os
import sys
import json
import csv
from pathlib import Path

def main():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ Error: DATABASE_URL environment variable not set")
        return 1
    
    # Read the seed data
    seed_file = os.path.join(os.path.dirname(__file__), '..', 'seeds', 'athlete_seed.json')
    if not os.path.exists(seed_file):
        print(f"❌ Error: Seed file not found at {seed_file}")
        return 1
    
    with open(seed_file, 'r') as f:
        athletes_data = json.load(f)
    
    print(f"📖 Loaded {len(athletes_data)} athletes from seed file")
    
    # Template mapping for new verification system
    # This maps athlete names to their template codes for the new URL format
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
    
    try:
        # Check if it's SQLite or PostgreSQL
        if database_url.startswith('sqlite'):
            import sqlite3
            # Extract the database file path
            db_path = database_url.replace('sqlite:///', '')
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
        else:
            import psycopg2
            from urllib.parse import urlparse
            
            # Parse database URL
            parsed = urlparse(database_url)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],  # Remove leading /
                user=parsed.username,
                password=parsed.password
            )
            cur = conn.cursor()
        
        # First, check what athletes exist in the database
        cur.execute("SELECT slug, full_name FROM athletes")
        existing_athletes = {row[0]: row[1] for row in cur.fetchall()}
        
        print(f"🔍 Found {len(existing_athletes)} existing athletes in database")
        
        # Sync athletes
        for athlete_data in athletes_data:
            slug = athlete_data['slug']
            name = athlete_data['full_name']
            
            if slug in existing_athletes:
                print(f"🔄 Syncing existing athlete: {name}")
            else:
                print(f"➕ Creating new athlete: {name}")
                # Insert new athlete with basic info first
                if database_url.startswith('sqlite'):
                    import uuid
                    athlete_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO athletes (id, slug, full_name, sport, created_at, updated_at)
                        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
                    """, (athlete_id, slug, name, athlete_data.get('sport', 'Archery')))
                else:
                    cur.execute("""
                        INSERT INTO athletes (id, slug, full_name, sport, created_at, updated_at)
                        VALUES (gen_random_uuid(), %s, %s, %s, NOW(), NOW())
                    """, (slug, name, athlete_data.get('sport', 'Archery')))
            
            # Update with all data
            cur.execute("""
                UPDATE athletes SET
                    full_name = %s,
                    sport = %s,
                    discipline = %s,
                    dob = %s,
                    nationality = %s,
                    hometown = %s,
                    handedness = %s,
                    world_ranking = %s,
                    best_world_ranking = %s,
                    intl_debut_year = %s,
                    bio_short = %s,
                    bio_long = %s,
                    quote_text = %s,
                    quote_source = %s,
                    card_image_url = %s,
                    card_back_url = %s,
                    hero_image_url = %s,
                    video_url = %s,
                    quote_photo_url = %s,
                    action_photo_url = %s,
                    qualification_image_url = %s,
                    gallery = %s,
                    socials = %s,
                    sponsors = %s,
                    updated_at = NOW()
                WHERE slug = %s
            """, (
                athlete_data['full_name'],
                athlete_data.get('sport', 'Archery'),
                athlete_data.get('discipline'),
                athlete_data.get('dob'),
                athlete_data.get('nationality'),
                athlete_data.get('hometown'),
                athlete_data.get('handedness'),
                athlete_data.get('world_ranking'),
                athlete_data.get('best_world_ranking'),
                athlete_data.get('intl_debut_year'),
                athlete_data.get('bio_short'),
                athlete_data.get('bio_long'),
                athlete_data.get('quote_text'),
                athlete_data.get('quote_source'),
                athlete_data.get('card_image_url'),
                athlete_data.get('card_back_url'),
                athlete_data.get('hero_image_url'),
                athlete_data.get('video_url'),
                athlete_data.get('quote_photo_url'),
                athlete_data.get('action_photo_url'),
                athlete_data.get('qualification_image_url'),
                json.dumps(athlete_data.get('gallery', [])),
                json.dumps(athlete_data.get('socials', {})),
                json.dumps(athlete_data.get('sponsors', [])),
                slug
            ))
        
        # Now create/update card templates with new verification system
        print("\n🎯 Creating/updating card templates for new verification system...")
        
        for athlete_data in athletes_data:
            name = athlete_data['full_name']
            slug = athlete_data['slug']
            
            # Get athlete ID
            cur.execute("SELECT id FROM athletes WHERE slug = %s", (slug,))
            athlete_result = cur.fetchone()
            if not athlete_result:
                print(f"⚠️  Skipping templates for {name} - athlete not found")
                continue
                
            athlete_id = athlete_result[0]
            
            # Create templates for both regular and diamond versions
            for version in ['regular', 'diamond']:
                template_code = athlete_template_mapping.get(name, {}).get(version)
                
                if not template_code:
                    print(f"⚠️  No template code found for {name} {version}")
                    continue
                
                # Check if template already exists
                cur.execute("""
                    SELECT id FROM card_templates 
                    WHERE athlete_id = %s AND version = %s
                """, (athlete_id, version))
                
                existing_template = cur.fetchone()
                
                if existing_template:
                    # Update existing template with new template_code
                    cur.execute("""
                        UPDATE card_templates 
                        SET template_code = %s, updated_at = NOW()
                        WHERE athlete_id = %s AND version = %s
                    """, (template_code, athlete_id, version))
                    print(f"🔄 Updated {name} {version} template with code {template_code}")
                else:
                    # Create new template
                    cur.execute("""
                        INSERT INTO card_templates (
                            id, athlete_id, version, template_code, minted_count, created_at, updated_at
                        ) VALUES (
                            gen_random_uuid(), %s, %s, %s, 0, NOW(), NOW()
                        )
                    """, (athlete_id, version, template_code))
                    print(f"➕ Created {name} {version} template with code {template_code}")
        
        conn.commit()
        print(f"\n✅ Successfully synced {len(athletes_data)} athletes and their templates")
        print("🔗 New verification URLs format: https://titansportshq.com/scan?t=000000000002")
        
        cur.close()
        conn.close()
        
        return 0
        
    except ImportError:
        print("❌ Error: psycopg2 not installed. Install with: pip install psycopg2-binary")
        return 1
    except Exception as e:
        print(f"❌ Error syncing athletes: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
