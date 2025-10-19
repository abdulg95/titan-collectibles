#!/usr/bin/env python3
"""
Update Brady Ellison's sponsors in the database.
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete
from app import app

def update_brady_sponsors():
    with app.app_context():
        brady = db.session.query(Athlete).filter_by(slug='brady-ellison').first()
        
        if brady:
            print(f"✅ Found Brady Ellison (ID: {brady.id})")
            
            # Update sponsors based on available logos
            brady.sponsors = [
                {
                    'name': 'Hoyt',
                    'logo_url': '/assets/sponsors/hoyt.png',
                    'url': 'https://hoyt.com'
                },
                {
                    'name': 'Easton',
                    'logo_url': '/assets/sponsors/easton.png',
                    'url': 'https://eastonarchery.com'
                },
                {
                    'name': 'TruBall',
                    'logo_url': '/assets/sponsors/truball.png',
                    'url': 'https://truball.com'
                },
                {
                    'name': 'Errea',
                    'logo_url': '/assets/sponsors/errea.png',
                    'url': 'https://www.errea.com'
                },
                {
                    'name': 'Spider Vanes',
                    'logo_url': '/assets/sponsors/spider-vanes.png',
                    'url': 'https://spidervanes.com'
                },
                {
                    'name': 'Shrewd',
                    'logo_url': '/assets/sponsors/shrewd.png',
                    'url': 'https://shrewdarchery.com'
                },
                {
                    'name': 'Lancaster',
                    'logo_url': '/assets/sponsors/lancaster.png',
                    'url': 'https://www.lancasterarchery.com'
                }
            ]
            
            db.session.commit()
            print(f"✅ Updated {len(brady.sponsors)} sponsors:")
            for sponsor in brady.sponsors:
                print(f"   - {sponsor['name']}: {sponsor['logo_url']}")
            print("\n🎯 Brady Ellison's sponsors updated successfully!")
        else:
            print("❌ Brady Ellison not found. Please ensure athlete data is loaded.")

if __name__ == '__main__':
    update_brady_sponsors()

