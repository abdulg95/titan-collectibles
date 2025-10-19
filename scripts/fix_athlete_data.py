#!/usr/bin/env python3
"""
Fix athlete data to match the expected values from the image/design
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
        
        # Fix specific athlete data based on the image requirements
        fixes = [
            {
                'slug': 'brady-ellison',
                'hometown': 'Glendale',
                'intl_debut_year': 2004,  # Career start should be 2004, not 2006
            },
            # Add more fixes as needed
        ]
        
        for fix in fixes:
            print(f"🔧 Fixing {fix['slug']}...")
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in fix.items():
                if key != 'slug':
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            values.append(fix['slug'])
            
            query = f"""
                UPDATE athletes SET {', '.join(set_clauses)}
                WHERE slug = %s
            """
            
            cur.execute(query, values)
            print(f"   ✅ Updated {len(set_clauses)} fields")
        
        conn.commit()
        print(f"✅ Successfully fixed {len(fixes)} athletes")
        
        # Also update the seed file with the correct data
        seed_file = os.path.join(os.path.dirname(__file__), '..', 'seeds', 'athlete_seed.json')
        if os.path.exists(seed_file):
            print("📝 Updating seed file with corrected data...")
            
            with open(seed_file, 'r') as f:
                athletes_data = json.load(f)
            
            # Update Brady Ellison's data
            for athlete in athletes_data:
                if athlete['slug'] == 'brady-ellison':
                    athlete['hometown'] = 'Glendale'
                    athlete['intl_debut_year'] = 2004
                    print("   ✅ Updated Brady Ellison in seed file")
                    break
            
            # Write back to file
            with open(seed_file, 'w') as f:
                json.dump(athletes_data, f, indent=2)
            
            print("   ✅ Seed file updated")
        
        cur.close()
        conn.close()
        
        return 0
        
    except ImportError:
        print("❌ Error: psycopg2 not installed. Install with: pip install psycopg2-binary")
        return 1
    except Exception as e:
        print(f"❌ Error fixing athlete data: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
