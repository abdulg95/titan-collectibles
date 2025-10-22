#!/usr/bin/env python3
"""
Fix existing card templates by setting their etrnl_url_group_id to match templates.csv
"""

import csv
from app import app, db
from models import CardTemplate, Athlete
from sqlalchemy.orm import joinedload


def fix_template_ids():
    """Update existing templates with correct etrnl_url_group_id from templates.csv"""
    with app.app_context():
        print("🔧 Fixing Card Template IDs:")
        
        # Read templates.csv
        templates_file_path = 'templates.csv'
        template_mapping = {}
        
        with open(templates_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create mapping by athlete name and version
                athlete_name = row['display_name'].split(' — ')[0].strip()
                version = row['version']
                template_id = row['template_id']
                sku = row['sku']
                
                key = f"{athlete_name}_{version}"
                template_mapping[key] = {
                    'template_id': template_id,
                    'sku': sku,
                    'display_name': row['display_name']
                }
        
        print(f"📊 Loaded {len(template_mapping)} template mappings from CSV")
        
        # Get all templates from database
        templates = CardTemplate.query.join(Athlete).options(joinedload(CardTemplate.athlete)).all()
        print(f"📊 Found {len(templates)} templates in database")
        
        updated_count = 0
        
        for template in templates:
            athlete_name = template.athlete.full_name
            version = template.version
            
            # Try different name variations
            # The CSV has names like "Sara Lopez - Regular" but DB has "Sara López"
            possible_keys = [
                f"{athlete_name}_{version}",
                f"{athlete_name.replace('ó', 'o')}_{version}",  # Sara López -> Sara Lopez
                f"{athlete_name.replace('í', 'i')}_{version}",  # Matias -> Mathias
                f"{athlete_name.replace('Matias', 'Mathias')}_{version}",  # Matias -> Mathias
                f"{athlete_name.replace('Sara López', 'Sara Lopez')}_{version}",  # Sara López -> Sara Lopez
                # Try with " - Regular" and " - Diamond" suffixes
                f"{athlete_name.replace('ó', 'o')} - Regular_{version}",
                f"{athlete_name.replace('ó', 'o')} - Diamond_{version}",
                f"{athlete_name.replace('Matias', 'Mathias')} - Regular_{version}",
                f"{athlete_name.replace('Matias', 'Mathias')} - Diamond_{version}",
            ]
            
            found_mapping = None
            for key in possible_keys:
                if key in template_mapping:
                    found_mapping = template_mapping[key]
                    break
            
            if found_mapping:
                old_id = template.etrnl_url_group_id
                template.etrnl_url_group_id = found_mapping['template_id']
                template.template_code = found_mapping['sku']
                
                print(f"  ✅ {athlete_name} ({version}): {old_id} → {found_mapping['template_id']} ({found_mapping['sku']})")
                updated_count += 1
            else:
                print(f"  ❌ No mapping found for: {athlete_name} ({version})")
                print(f"      Tried keys: {possible_keys}")
                print(f"      Available keys: {list(template_mapping.keys())}")
        
        db.session.commit()
        print(f"\n🎉 Successfully updated {updated_count} template IDs!")


if __name__ == '__main__':
    fix_template_ids()
