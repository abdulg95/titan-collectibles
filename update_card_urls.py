#!/usr/bin/env python3
"""
Script to update card templates with new verification URLs.
This script updates the template_code field to use the new titansportshq.com format.
"""

import sys
import os
sys.path.append('.')

from app import app
from models import db, CardTemplate, Athlete

def update_card_urls():
    """Update card template URLs to use the new titansportshq.com format."""
    
    with app.app_context():
        print("Updating card template URLs...")
        
        # Get all card templates
        templates = db.session.query(CardTemplate).all()
        
        if not templates:
            print("No card templates found in database.")
            return
        
        updated_count = 0
        
        for template in templates:
            athlete = db.session.get(Athlete, template.athlete_id)
            
            # The template_code should be the template_id from the CSV
            # which corresponds to the URL parameter (t=000000000002)
            if template.template_code:
                print(f"Template {template.id} already has template_code: {template.template_code}")
                continue
            
            # Map athlete names to template IDs based on the CSV
            athlete_template_mapping = {
                'Brady Ellison': {
                    'regular': '000000000001',
                    'diamond': '000000000002'
                },
                'Mete Gazoz': {
                    'regular': '000000000003', 
                    'diamond': '000000000004'
                },
                'Ella Gibson': {
                    'regular': '000000000005',
                    'diamond': '000000000006'
                },
                'Deepika Kumari': {
                    'regular': '000000000007',
                    'diamond': '000000000008'
                },
                'Sara López': {
                    'regular': '000000000009',
                    'diamond': '000000000010'
                },
                'Mike Schloesser': {
                    'regular': '000000000011',
                    'diamond': '000000000012'
                },
                'Lim Sihyeon': {
                    'regular': '000000000013',
                    'diamond': '000000000014'
                },
                'Mathias Fullerton': {
                    'regular': '000000000015',
                    'diamond': '000000000016'
                },
                'Kim Woojin': {
                    'regular': '000000000017',
                    'diamond': '000000000018'
                }
            }
            
            if athlete and athlete.full_name in athlete_template_mapping:
                template_id = athlete_template_mapping[athlete.full_name].get(template.version)
                if template_id:
                    template.template_code = template_id
                    print(f"Updated {athlete.full_name} {template.version}: {template_id}")
                    updated_count += 1
                else:
                    print(f"No template ID found for {athlete.full_name} {template.version}")
            else:
                print(f"Unknown athlete: {athlete.full_name if athlete else 'None'}")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\nSuccessfully updated {updated_count} card templates.")
            print("\nNew card URLs will be in format: https://titansportshq.com/scan?t=000000000002")
        else:
            print("No templates were updated.")

if __name__ == "__main__":
    update_card_urls()
