#!/usr/bin/env python3
"""
Update Brady Ellison's card back URL in the database.
"""

import os
import sys

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete
from app import app

def update_brady_card_back():
    with app.app_context():
        brady = db.session.query(Athlete).filter_by(slug='brady-ellison').first()
        
        if brady:
            print(f"✅ Found Brady Ellison (ID: {brady.id})")
            
            # Update card back URL
            brady.card_back_url = "/assets/cards-back/BE.png"
            
            db.session.commit()
            print(f"✅ Updated card back URL: {brady.card_back_url}")
            print("\n🎯 Brady Ellison's card back updated successfully!")
        else:
            print("❌ Brady Ellison not found. Please ensure athlete data is loaded.")

if __name__ == '__main__':
    update_brady_card_back()

