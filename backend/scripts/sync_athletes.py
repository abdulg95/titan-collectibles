#!/usr/bin/env python3
"""
Comprehensive sync of athlete data from seed file to database
"""

import os
import sys
import json

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
    
    try:
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
        
        for athlete_data in athletes_data:
            slug = athlete_data['slug']
            name = athlete_data['full_name']
            
            if slug in existing_athletes:
                print(f"🔄 Syncing existing athlete: {name}")
            else:
                print(f"➕ Creating new athlete: {name}")
                # Insert new athlete with basic info first
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
                    hero_image_url = %s,
                    video_url = %s,
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
                athlete_data.get('hero_image_url'),
                athlete_data.get('video_url'),
                json.dumps(athlete_data.get('gallery', [])),
                json.dumps(athlete_data.get('socials', {})),
                json.dumps(athlete_data.get('sponsors', [])),
                slug
            ))
        
        conn.commit()
        print(f"✅ Successfully synced {len(athletes_data)} athletes")
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
