#!/usr/bin/env python3
"""
Update Brady Ellison's social media links in the database.
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete
from app import app

def update_brady_socials():
    with app.app_context():
        brady = db.session.query(Athlete).filter_by(slug='brady-ellison').first()
        
        if brady:
            print(f"✅ Found Brady Ellison (ID: {brady.id})")
            
            # Update social media links
            brady.socials = {
                'instagram': 'https://www.instagram.com/bradyellison',
                'facebook': 'https://www.facebook.com/Ellisonarcherypowercouple/'
            }
            
            db.session.commit()
            print(f"✅ Updated social media links:")
            print(f"   Instagram: {brady.socials.get('instagram')}")
            print(f"   Facebook: {brady.socials.get('facebook')}")
            print("\n🎯 Brady Ellison's social media links updated successfully!")
        else:
            print("❌ Brady Ellison not found. Please ensure athlete data is loaded.")

if __name__ == '__main__':
    update_brady_socials()

