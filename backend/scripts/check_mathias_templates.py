#!/usr/bin/env python3
"""
Check Mathias Fullerton's templates and cards.
"""

import os
import sys

# Add the parent directory to the path so we can import from the backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Athlete, CardTemplate, CardInstance
from app import app

def check_mathias_templates():
    with app.app_context():
        mathias = db.session.query(Athlete).filter_by(slug='mathias-fullerton').first()
        
        if not mathias:
            print("❌ Mathias Fullerton not found in database!")
            return
        
        print(f"✅ Found Mathias Fullerton (ID: {mathias.id})")
        
        # Find templates for Mathias
        templates = db.session.query(CardTemplate).filter_by(athlete_id=mathias.id).all()
        
        print(f"\n📇 Templates for Mathias: {len(templates)}")
        for tpl in templates:
            print(f"\n   Template ID: {tpl.id}")
            print(f"   Version: {tpl.version}")
            print(f"   SKU: {tpl.sku}")
            print(f"   Template Code: {tpl.template_code}")
            print(f"   Minted: {tpl.minted_count}/{tpl.edition_cap}")
            
            # Check card instances for this template
            instances = db.session.query(CardInstance).filter_by(template_id=tpl.id).all()
            print(f"   Card Instances: {len(instances)}")
            
            if instances:
                for inst in instances[:3]:  # Show first 3
                    print(f"      - Card ID: {inst.id}, Serial: {inst.serial_no}, Status: {inst.status}")

if __name__ == '__main__':
    check_mathias_templates()

