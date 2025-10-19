#!/usr/bin/env python3
"""
Fix Mathias Fullerton templates to point to the correct athlete record.
"""

import os
import sys

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete, CardTemplate, CardInstance
from app import app

def fix_mathias_templates():
    with app.app_context():
        # Find the old "Matias" entry (without h)
        old_matias = db.session.query(Athlete).filter_by(slug='matias-fullerton').first()
        
        # Find the correct "Mathias" entry (with h)
        correct_mathias = db.session.query(Athlete).filter_by(slug='mathias-fullerton').first()
        
        if not old_matias:
            print("ℹ️  No old 'Matias' record found - might already be fixed")
            return
        
        if not correct_mathias:
            print("❌ Correct 'Mathias' record not found!")
            return
        
        print(f"✅ Found old Matias (ID: {old_matias.id})")
        print(f"✅ Found correct Mathias (ID: {correct_mathias.id})")
        
        # Find all templates linked to old Matias
        old_templates = db.session.query(CardTemplate).filter_by(athlete_id=old_matias.id).all()
        
        print(f"\n📇 Found {len(old_templates)} templates linked to old Matias")
        
        for tpl in old_templates:
            print(f"   Updating template {tpl.template_code} ({tpl.version})")
            tpl.athlete_id = correct_mathias.id
        
        # Delete the old Matias record
        print(f"\n🗑️  Deleting old 'Matias' record...")
        db.session.delete(old_matias)
        
        db.session.commit()
        print(f"\n✅ Successfully updated all templates to point to correct Mathias!")
        print(f"✅ Deleted old 'Matias' record")

if __name__ == '__main__':
    fix_mathias_templates()

