#!/usr/bin/env python3
"""
Generate all available cards for a specific user without increasing mint count.
This is for testing purposes to see all cards and possible issues in production.

Usage:
  python scripts/generate_all_cards_for_user.py --email abdulg1995@gmail.com
"""

import argparse
import uuid as _uuid
from datetime import datetime, timezone
import random
import string

from app import app, db
from models import (
    User, Athlete, CardTemplate, CardInstance, ScanEvent,
    CardStatus
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload


def rand_tag(prefix="TEST"):
    # Short, human-readable fake tag id & uid for testing
    r = ''.join(random.choices(string.digits, k=6))
    uid = ''.join(random.choices('0123456789ABCDEF', k=14))
    return f"{prefix}-{r}", f"UID-{uid}"


def generate_all_cards_for_user(email: str):
    """Generate all available card templates for a specific user"""
    with app.app_context():
        # Find the user
        user = User.query.filter_by(email=email.strip().lower()).first()
        if not user:
            raise SystemExit(f"ERROR: No user found with email {email}")
        
        print(f"🎯 Generating all cards for user: {user.email} ({user.id})")
        
        # Get all card templates
        templates = CardTemplate.query.join(Athlete).options(joinedload(CardTemplate.athlete)).all()
        print(f"📊 Found {len(templates)} card templates")
        
        created = []
        skipped = []
        
        for template in templates:
            print(f"\n🔄 Processing template: {template.athlete.full_name} ({template.version})")
            print(f"  Template ID: {template.id}")
            print(f"  Template Code: {getattr(template, 'template_code', 'N/A')}")
            print(f"  Current minted_count: {template.minted_count}")
            print(f"  Edition cap: {template.edition_cap}")
            
            # Check if user already has this template
            existing_card = CardInstance.query.filter_by(
                template_id=template.id,
                owner_user_id=user.id
            ).first()
            
            if existing_card:
                print(f"  ⏭️  User already has this card (serial: {existing_card.serial_no})")
                skipped.append(template)
                continue
            
            # Create the card instance WITHOUT increasing minted_count
            # Use athlete slug or fallback to first 3 chars of name
            prefix = template.athlete.slug[:3].upper() if template.athlete.slug else template.athlete.full_name[:3].upper()
            tag_id, uid = rand_tag(prefix=prefix)
            
            # Use current minted_count + 1 for serial, but don't update minted_count
            next_serial = (template.minted_count or 0) + 1
            
            inst = CardInstance(
                template_id=template.id,
                serial_no=next_serial,
                etrnl_tag_uid=uid,
                etrnl_tag_id=tag_id,
                last_ctr=1,  # pretend first scan already happened
                owner_user_id=user.id,
                status=CardStatus.claimed,
            )
            db.session.add(inst)
            
            # Add a "successful scan" event for the audit trail
            db.session.add(ScanEvent(
                card_instance_id=inst.id,
                tag_id=tag_id,
                uid=uid,
                ctr=1,
                authentic=True,
                tt_curr="ok",
                tt_perm="ok",
                ip="127.0.0.1",
                user_agent="generate-all-cards/1.0",
                created_at=datetime.now(timezone.utc)
            ))
            
            created.append((template, inst))
            print(f"  ✅ Created CardInstance {inst.id} (serial: {inst.serial_no})")
        
        db.session.commit()
        
        print(f"\n🎉 Summary:")
        print(f"  ✅ Created: {len(created)} new cards")
        print(f"  ⏭️  Skipped: {len(skipped)} cards (user already had them)")
        
        print(f"\n📋 Created cards:")
        for template, inst in created:
            print(f"  - {template.athlete.full_name} ({template.version}) - Serial: {inst.serial_no}")
        
        if skipped:
            print(f"\n📋 Skipped cards (user already had them):")
            for template in skipped:
                print(f"  - {template.athlete.full_name} ({template.version})")


def main():
    p = argparse.ArgumentParser(description="Generate all available cards for a user (testing)")
    p.add_argument("--email", required=True, help="User email to generate cards for")
    args = p.parse_args()
    
    generate_all_cards_for_user(args.email)


if __name__ == "__main__":
    main()
