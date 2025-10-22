#!/usr/bin/env python3
"""
Check user's card collection and identify missing cards and broken images.
"""

from app import app, db
from models import User, CardInstance, CardTemplate, Athlete
from sqlalchemy.orm import joinedload


def check_user_cards():
    """Check user's card collection"""
    with app.app_context():
        user = User.query.filter_by(email='abdulg1995@gmail.com').first()
        if not user:
            print('User not found')
            return
        
        print(f'User: {user.email}')
        
        # Get all card instances for this user
        cards = CardInstance.query.filter_by(owner_user_id=user.id).options(
            joinedload(CardInstance.template).joinedload(CardTemplate.athlete)
        ).all()
        
        print(f'Total cards: {len(cards)}')
        
        # Group by athlete and version
        by_athlete = {}
        for card in cards:
            if card.template and card.template.athlete:
                athlete_name = card.template.athlete.full_name
                version = card.template.version
                card_number = card.template.athlete.card_number
                
                if athlete_name not in by_athlete:
                    by_athlete[athlete_name] = {}
                by_athlete[athlete_name][version] = {
                    'card_number': card_number,
                    'serial': card.serial_no,
                    'template_code': card.template.template_code,
                    'image_url': card.template.image_url,
                    'athlete_card_image_url': card.template.athlete.card_image_url
                }
        
        # Print sorted by card number
        sorted_athletes = sorted(by_athlete.items(), key=lambda x: x[1]['regular']['card_number'] if 'regular' in x[1] else x[1]['diamond']['card_number'])
        
        print("\n=== USER'S CARD COLLECTION ===")
        for athlete_name, versions in sorted_athletes:
            card_number = versions['regular']['card_number'] if 'regular' in versions else versions['diamond']['card_number']
            print(f'\nCard #{card_number}: {athlete_name}')
            
            for version in ['regular', 'diamond']:
                if version in versions:
                    v = versions[version]
                    print(f'  {version}: Serial {v["serial"]} - {v["template_code"]}')
                    print(f'    Template image_url: {v["image_url"]}')
                    print(f'    Athlete card_image_url: {v["athlete_card_image_url"]}')
                else:
                    print(f'  {version}: MISSING')
        
        # Check for missing card numbers
        print("\n=== MISSING CARD NUMBERS ===")
        expected_numbers = set(range(1, 9))  # Cards 1-8
        actual_numbers = set()
        for athlete_name, versions in by_athlete.items():
            card_number = versions['regular']['card_number'] if 'regular' in versions else versions['diamond']['card_number']
            actual_numbers.add(card_number)
        
        missing_numbers = expected_numbers - actual_numbers
        if missing_numbers:
            print(f"Missing card numbers: {sorted(missing_numbers)}")
        else:
            print("All card numbers 1-8 are present")
        
        # Check for broken images
        print("\n=== BROKEN IMAGES CHECK ===")
        broken_images = []
        for athlete_name, versions in by_athlete.items():
            for version in ['regular', 'diamond']:
                if version in versions:
                    v = versions[version]
                    template_url = v['image_url']
                    athlete_url = v['athlete_card_image_url']
                    
                    if not template_url or template_url == '/assets/cards/.png':
                        broken_images.append(f"{athlete_name} ({version}) - Template image_url: {template_url}")
                    if not athlete_url or athlete_url == '/assets/cards/':
                        broken_images.append(f"{athlete_name} ({version}) - Athlete card_image_url: {athlete_url}")
        
        if broken_images:
            print("Broken images found:")
            for broken in broken_images:
                print(f"  - {broken}")
        else:
            print("No broken images found")


if __name__ == '__main__':
    check_user_cards()
