#!/usr/bin/env python3
"""
Load athlete achievements from athlete_seed.json into the database.
"""

import os
import json
import psycopg2
import uuid
from urllib.parse import urlparse

def load_achievements():
    # Load seed data
    with open('seeds/athlete_seed.json', 'r') as f:
        athletes_data = json.load(f)
    
    # Connect to database
    parsed = urlparse(os.environ['DATABASE_URL'])
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password
    )
    cur = conn.cursor()
    
    try:
        for athlete_data in athletes_data:
            slug = athlete_data.get('slug')
            if not slug:
                continue
                
            # Get athlete ID
            cur.execute('SELECT id FROM athletes WHERE slug = %s', (slug,))
            athlete_row = cur.fetchone()
            if not athlete_row:
                print(f'⚠️  Athlete not found: {slug}')
                continue
                
            athlete_id = athlete_row[0]
            
            # Clear existing achievements
            cur.execute('DELETE FROM athlete_achievements WHERE athlete_id = %s', (athlete_id,))
            
            # Load achievements
            achievements = athlete_data.get('achievements', [])
            if not achievements:
                print(f'📝 No achievements for {athlete_data.get("full_name", slug)}')
                continue
                
            for i, achievement in enumerate(achievements):
                # Handle both object and string formats
                if isinstance(achievement, dict):
                    title = achievement.get('title')
                    result = achievement.get('result')
                    medal = achievement.get('medal', 'none')
                    display_order = achievement.get('display_order', 0)
                elif isinstance(achievement, str):
                    # Handle string format like "olympic_games:"
                    title = achievement.replace(':', '').replace('_', ' ').title()
                    result = "Achievement"
                    medal = 'none'
                    display_order = i
                else:
                    print(f'⚠️  Skipping unknown achievement format: {achievement}')
                    continue
                
                cur.execute('''
                    INSERT INTO athlete_achievements 
                    (id, athlete_id, title, result, medal, display_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    str(uuid.uuid4()),
                    athlete_id,
                    title,
                    result,
                    medal,
                    display_order
                ))
            
            print(f'✅ Loaded {len(achievements)} achievements for {athlete_data.get("full_name", slug)}')
        
        conn.commit()
        print('🎉 All achievements loaded successfully!')
        
    except Exception as e:
        conn.rollback()
        print(f'❌ Error: {e}')
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    load_achievements()
