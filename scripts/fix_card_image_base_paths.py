#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Athlete

def fix_card_image_base_paths():
    """Fix card image URLs to use base paths (without extensions) as expected by routes_cards.py"""
    with app.app_context():
        print("🔧 Fixing Card Image Base Paths:")
        
        # Fix Deepika Kumari
        print(f"\n📊 Fixing Deepika Kumari:")
        deepika = Athlete.query.filter_by(full_name='Deepika Kumari').first()
        if deepika:
            # Update athlete card image URL to base path (backend will append -REG.png or -DIA.png)
            deepika.card_image_url = '/assets/cards/DK'
            print(f"  ✅ Updated athlete card_image_url: {deepika.card_image_url}")
        else:
            print("  ❌ Deepika Kumari not found")
        
        # Fix Mathias Fullerton
        print(f"\n📊 Fixing Mathias Fullerton:")
        mathias = Athlete.query.filter_by(full_name='Mathias Fullerton').first()
        if mathias:
            # Update athlete card image URL to base path (backend will append -REG.png or -DIA.png)
            mathias.card_image_url = '/assets/cards/MF'
            print(f"  ✅ Updated athlete card_image_url: {mathias.card_image_url}")
        else:
            print("  ❌ Mathias Fullerton not found")
        
        # Commit changes
        db.session.commit()
        print(f"\n🎉 Successfully fixed card image base paths!")

if __name__ == '__main__':
    fix_card_image_base_paths()
