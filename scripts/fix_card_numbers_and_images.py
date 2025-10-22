#!/usr/bin/env python3
"""
Fix card numbers and image URLs for athletes.
"""

from app import app, db
from models import Athlete, CardTemplate


def fix_card_numbers_and_images():
    """Fix card numbers and image URLs"""
    with app.app_context():
        print("🔧 Fixing Card Numbers and Image URLs:")
        
        # Fix card numbers based on templates.csv order
        fixes = [
            ("Brady Ellison", 1, "BE"),
            ("Mathias Fullerton", 2, "MF"), 
            ("Mete Gazoz", 3, "MG"),
            ("Ella Gibson", 4, "EG"),
            ("Deepika Kumari", 5, "DK"),
            ("Sara López", 6, "SL"),
            ("Mike Schloesser", 7, "MS"),
            ("Lim Sihyeon", 8, "LS"),
            ("Kim Woojin", 9, "KW"),
        ]
        
        for athlete_name, card_number, prefix in fixes:
            athlete = Athlete.query.filter_by(full_name=athlete_name).first()
            if not athlete:
                print(f"  ❌ Athlete not found: {athlete_name}")
                continue
            
            # Fix card number
            old_card_number = athlete.card_number
            athlete.card_number = card_number
            print(f"  ✅ {athlete_name}: Card number {old_card_number} → {card_number}")
            
            # Fix athlete card_image_url (base path without extension)
            athlete.card_image_url = f"/assets/cards/{prefix}"
            print(f"  ✅ {athlete_name}: Set card_image_url = {athlete.card_image_url}")
            
            # Fix template image URLs
            templates = CardTemplate.query.filter_by(athlete_id=athlete.id).all()
            for template in templates:
                if template.version == 'regular':
                    template.image_url = f"/assets/cards/{prefix}-REG.png"
                    print(f"  ✅ {athlete_name} ({template.version}): Set image_url = {template.image_url}")
                elif template.version == 'diamond':
                    template.image_url = f"/assets/cards/{prefix}-DIA.png"
                    print(f"  ✅ {athlete_name} ({template.version}): Set image_url = {template.image_url}")
        
        db.session.commit()
        print("\n🎉 Successfully fixed all card numbers and image URLs!")


if __name__ == '__main__':
    fix_card_numbers_and_images()
