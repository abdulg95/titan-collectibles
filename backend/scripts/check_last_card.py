#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, CardInstance, Athlete, CardTemplate

def check_last_registered_card():
    """Check the last registered card instance"""
    with app.app_context():
        # Get the most recent card instance
        last_card = CardInstance.query.order_by(CardInstance.created_at.desc()).first()
        
        if not last_card:
            print("No card instances found in database")
            return
        
        print(f"📊 Last Registered Card:")
        print(f"  Card Instance ID: {last_card.id}")
        print(f"  Created At: {last_card.created_at}")
        print(f"  Status: {last_card.status}")
        print(f"  NFC Tag ID: {last_card.nfc_tag_id}")
        
        # Get athlete info
        if last_card.card_template:
            athlete = last_card.card_template.athlete
            if athlete:
                print(f"  Athlete: {athlete.full_name}")
                print(f"  Card Number: {athlete.card_number}")
                print(f"  Template Version: {last_card.card_template.version}")
            else:
                print(f"  Template ID: {last_card.card_template_id}")
                print(f"  Athlete: Not found")
        else:
            print(f"  Template ID: {last_card.card_template_id}")
            print(f"  Template: Not found")
        
        # Get user info if available
        if last_card.user:
            print(f"  Registered by: {last_card.user.email}")
        else:
            print(f"  User ID: {last_card.user_id}")
            print(f"  User: Not found")
        
        print(f"\n📋 Recent Card Instances (last 5):")
        recent_cards = CardInstance.query.order_by(CardInstance.created_at.desc()).limit(5).all()
        
        for i, card in enumerate(recent_cards, 1):
            athlete_name = "Unknown"
            if card.card_template and card.card_template.athlete:
                athlete_name = card.card_template.athlete.full_name
            
            user_email = "Unknown"
            if card.user:
                user_email = card.user.email
            
            print(f"  {i}. {card.created_at} - {athlete_name} ({card.status}) - {user_email}")

if __name__ == '__main__':
    check_last_registered_card()
