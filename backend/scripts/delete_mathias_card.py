#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, CardInstance, ScanEvent, CardTemplate, Athlete

def delete_mathias_card():
    """Delete the incorrectly programmed Mathias card instance"""
    with app.app_context():
        # Find the Mathias card instance
        mathias_card = CardInstance.query.join(CardTemplate).join(Athlete).filter(
            Athlete.full_name == 'Mathias Fullerton'
        ).order_by(CardInstance.created_at.desc()).first()
        
        if not mathias_card:
            print("No Mathias Fullerton card found")
            return
        
        print(f"🗑️ Deleting Mathias Fullerton Card:")
        print(f"  Card Instance ID: {mathias_card.id}")
        print(f"  Created At: {mathias_card.created_at}")
        print(f"  Status: {mathias_card.status}")
        print(f"  ETRNL Tag ID: {mathias_card.etrnl_tag_id}")
        print(f"  Template Code: {mathias_card.template.template_code}")
        print(f"  Template Version: {mathias_card.template.version}")
        
        # Delete associated scan events first
        scan_events = ScanEvent.query.filter_by(card_instance_id=mathias_card.id).all()
        print(f"\n🔍 Found {len(scan_events)} scan events to delete:")
        for event in scan_events:
            print(f"  - Scan Event ID: {event.id} ({event.created_at})")
            db.session.delete(event)
        
        # Delete the card instance
        db.session.delete(mathias_card)
        
        # Commit the changes
        db.session.commit()
        
        print(f"\n✅ Successfully deleted Mathias Fullerton card instance and {len(scan_events)} scan events")
        
        # Verify deletion
        remaining_cards = CardInstance.query.join(CardTemplate).join(Athlete).filter(
            Athlete.full_name == 'Mathias Fullerton'
        ).count()
        print(f"📊 Remaining Mathias Fullerton cards: {remaining_cards}")

if __name__ == '__main__':
    delete_mathias_card()
