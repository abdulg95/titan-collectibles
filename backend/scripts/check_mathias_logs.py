#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, CardInstance, ScanEvent, CardTemplate, Athlete

def check_mathias_card_logs():
    """Check logs and scan events for the Mathias card"""
    with app.app_context():
        # Find the Mathias card instance
        mathias_card = CardInstance.query.join(CardInstance.template).join(CardTemplate.athlete).filter(
            Athlete.full_name == 'Mathias Fullerton'
        ).order_by(CardInstance.created_at.desc()).first()
        
        if not mathias_card:
            print("No Mathias Fullerton card found")
            return
        
        print(f"📊 Mathias Fullerton Card Details:")
        print(f"  Card Instance ID: {mathias_card.id}")
        print(f"  Created At: {mathias_card.created_at}")
        print(f"  Status: {mathias_card.status}")
        print(f"  ETRNL Tag ID: {mathias_card.etrnl_tag_id}")
        print(f"  ETRNL Tag UID: {mathias_card.etrnl_tag_uid}")
        
        # Check for scan events related to this card
        print(f"\n🔍 Scan Events for this card:")
        scan_events = ScanEvent.query.filter_by(card_instance_id=mathias_card.id).order_by(ScanEvent.created_at.desc()).all()
        
        if scan_events:
            for i, event in enumerate(scan_events, 1):
                print(f"  {i}. Scan Event ID: {event.id}")
                print(f"     Created At: {event.created_at}")
                print(f"     Tag ID: {event.tag_id}")
                print(f"     UID: {event.uid}")
                print(f"     Authentic: {event.authentic}")
                print(f"     IP: {event.ip}")
                print(f"     User Agent: {event.user_agent}")
                print(f"     CTR: {event.ctr}")
                print(f"     TT Current: {event.tt_curr}")
                print(f"     TT Permanent: {event.tt_perm}")
                print()
        else:
            print("  No scan events found for this card")
        
        # Check for any scan events with the same tag ID/UID
        print(f"\n🔍 All Scan Events with Tag ID '{mathias_card.etrnl_tag_id}':")
        related_scans = ScanEvent.query.filter(
            (ScanEvent.tag_id == mathias_card.etrnl_tag_id) | 
            (ScanEvent.uid == mathias_card.etrnl_tag_uid)
        ).order_by(ScanEvent.created_at.desc()).all()
        
        if related_scans:
            for i, scan in enumerate(related_scans, 1):
                print(f"  {i}. Scan Event ID: {scan.id}")
                print(f"     Created At: {scan.created_at}")
                print(f"     Card Instance ID: {scan.card_instance_id}")
                print(f"     Tag ID: {scan.tag_id}")
                print(f"     UID: {scan.uid}")
                print(f"     Authentic: {scan.authentic}")
                print(f"     IP: {scan.ip}")
                print(f"     User Agent: {scan.user_agent}")
                print()
        else:
            print("  No related scan events found")

if __name__ == '__main__':
    check_mathias_card_logs()
