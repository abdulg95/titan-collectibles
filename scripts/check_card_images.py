#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, CardInstance, CardTemplate, Athlete

def check_card_images():
    """Check card images for Deepika and Mathias"""
    with app.app_context():
        print("🔍 Checking Card Images and Data:")
        
        # Check Deepika Kumari
        print(f"\n📊 Deepika Kumari:")
        deepika = Athlete.query.filter_by(full_name='Deepika Kumari').first()
        if deepika:
            print(f"  Athlete ID: {deepika.id}")
            print(f"  Card Number: {deepika.card_number}")
            print(f"  Card Image URL: {deepika.card_image_url}")
            print(f"  Card Back URL: {deepika.card_back_url}")
            print(f"  Hero Image URL: {deepika.hero_image_url}")
            print(f"  Sponsors: {len(deepika.sponsors) if deepika.sponsors else 0} items")
            print(f"  Socials: {len(deepika.socials) if deepika.socials else 0} items")
            
            # Check her card templates
            templates = CardTemplate.query.filter_by(athlete_id=deepika.id).all()
            for template in templates:
                print(f"    Template {template.id} ({template.version}): Image URL = {template.image_url}")
        else:
            print("  ❌ Deepika Kumari not found")
        
        # Check Mathias Fullerton
        print(f"\n📊 Mathias Fullerton:")
        mathias = Athlete.query.filter_by(full_name='Mathias Fullerton').first()
        if mathias:
            print(f"  Athlete ID: {mathias.id}")
            print(f"  Card Number: {mathias.card_number}")
            print(f"  Card Image URL: {mathias.card_image_url}")
            print(f"  Card Back URL: {mathias.card_back_url}")
            print(f"  Hero Image URL: {mathias.hero_image_url}")
            print(f"  Sponsors: {len(mathias.sponsors) if mathias.sponsors else 0} items")
            print(f"  Socials: {len(mathias.socials) if mathias.socials else 0} items")
            
            # Check his card templates
            templates = CardTemplate.query.filter_by(athlete_id=mathias.id).all()
            for template in templates:
                print(f"    Template {template.id} ({template.version}): Image URL = {template.image_url}")
        else:
            print("  ❌ Mathias Fullerton not found")
        
        # Check if there are any card instances for these athletes
        print(f"\n📋 Card Instances:")
        deepika_cards = CardInstance.query.join(CardTemplate).join(Athlete).filter(
            Athlete.full_name == 'Deepika Kumari'
        ).all()
        print(f"  Deepika Kumari cards: {len(deepika_cards)}")
        
        mathias_cards = CardInstance.query.join(CardTemplate).join(Athlete).filter(
            Athlete.full_name == 'Mathias Fullerton'
        ).all()
        print(f"  Mathias Fullerton cards: {len(mathias_cards)}")

if __name__ == '__main__':
    check_card_images()
