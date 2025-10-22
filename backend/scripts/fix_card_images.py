#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, CardTemplate, Athlete

def fix_card_images():
    """Fix broken card image URLs"""
    with app.app_context():
        print("🔧 Fixing Card Image URLs:")
        
        # Fix Deepika Kumari
        print(f"\n📊 Fixing Deepika Kumari:")
        deepika = Athlete.query.filter_by(full_name='Deepika Kumari').first()
        if deepika:
            # Update athlete card image URL
            deepika.card_image_url = '/assets/cards/DK-REG.png'
            print(f"  ✅ Updated athlete card_image_url: {deepika.card_image_url}")
            
            # Update her card templates
            templates = CardTemplate.query.filter_by(athlete_id=deepika.id).all()
            for template in templates:
                if template.version == 'diamond':
                    template.image_url = '/assets/cards/DK-DIA.png'
                    print(f"  ✅ Updated diamond template {template.id}: {template.image_url}")
                elif template.version == 'regular':
                    template.image_url = '/assets/cards/DK-REG.png'
                    print(f"  ✅ Updated regular template {template.id}: {template.image_url}")
        else:
            print("  ❌ Deepika Kumari not found")
        
        # Fix Mathias Fullerton
        print(f"\n📊 Fixing Mathias Fullerton:")
        mathias = Athlete.query.filter_by(full_name='Mathias Fullerton').first()
        if mathias:
            # Update athlete card image URL
            mathias.card_image_url = '/assets/cards/MF-REG.png'
            print(f"  ✅ Updated athlete card_image_url: {mathias.card_image_url}")
            
            # Update his card templates
            templates = CardTemplate.query.filter_by(athlete_id=mathias.id).all()
            for template in templates:
                if template.version == 'diamond':
                    template.image_url = '/assets/cards/MF-DIA.png'
                    print(f"  ✅ Updated diamond template {template.id}: {template.image_url}")
                elif template.version == 'regular':
                    template.image_url = '/assets/cards/MF-REG.png'
                    print(f"  ✅ Updated regular template {template.id}: {template.image_url}")
        else:
            print("  ❌ Mathias Fullerton not found")
        
        # Commit changes
        db.session.commit()
        print(f"\n🎉 Successfully fixed all card image URLs!")

if __name__ == '__main__':
    fix_card_images()
