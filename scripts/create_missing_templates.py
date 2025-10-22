#!/usr/bin/env python3
"""
Create missing card templates for athletes that don't have them yet.
Based on templates.csv, we need to create templates for:
- Brady Ellison (regular & diamond)
- Mike Schloesser (regular & diamond) 
- Lim Sihyeon (regular & diamond)
"""

import csv
import uuid
from app import app, db
from models import Athlete, CardTemplate
from sqlalchemy.orm import joinedload


def create_missing_templates():
    """Create missing card templates for athletes"""
    with app.app_context():
        print("🔧 Creating Missing Card Templates:")
        
        # Read templates.csv to get the missing template info
        templates_file_path = 'templates.csv'
        missing_templates = []
        
        with open(templates_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                athlete_name = row['display_name'].split(' — ')[0].strip()
                version = row['version']
                template_id = row['template_id']
                sku = row['sku']
                
                missing_templates.append({
                    'athlete_name': athlete_name,
                    'version': version,
                    'template_id': template_id,
                    'sku': sku,
                    'display_name': row['display_name']
                })
        
        print(f"📊 Loaded {len(missing_templates)} template definitions from CSV")
        
        # Get all athletes
        athletes = Athlete.query.all()
        athlete_map = {athlete.full_name: athlete for athlete in athletes}
        
        print(f"📊 Found {len(athletes)} athletes in database")
        
        created_count = 0
        
        for template_info in missing_templates:
            athlete_name = template_info['athlete_name']
            version = template_info['version']
            template_id = template_info['template_id']
            sku = template_info['sku']
            
            # Handle name variations
            athlete = None
            possible_names = [
                athlete_name,
                athlete_name.replace('ó', 'o'),  # Sara López -> Sara Lopez
                athlete_name.replace('Matias', 'Mathias'),  # Matias -> Mathias
                # Remove " - Regular" and " - Diamond" suffixes
                athlete_name.replace(' - Regular', ''),
                athlete_name.replace(' - Diamond', ''),
                athlete_name.replace('ó', 'o').replace(' - Regular', ''),
                athlete_name.replace('ó', 'o').replace(' - Diamond', ''),
                athlete_name.replace('Matias', 'Mathias').replace(' - Regular', ''),
                athlete_name.replace('Matias', 'Mathias').replace(' - Diamond', ''),
                # Handle Sara López specifically
                athlete_name.replace('Sara Lopez', 'Sara López'),
                athlete_name.replace('Sara Lopez - Regular', 'Sara López'),
                athlete_name.replace('Sara Lopez - Diamond', 'Sara López'),
            ]
            
            for name in possible_names:
                if name in athlete_map:
                    athlete = athlete_map[name]
                    break
            
            if not athlete:
                print(f"  ❌ Athlete not found: {athlete_name}")
                continue
            
            # Check if template already exists
            existing_template = CardTemplate.query.filter_by(
                athlete_id=athlete.id,
                version=version
            ).first()
            
            if existing_template:
                print(f"  ⏭️  Template already exists: {athlete.full_name} ({version})")
                continue
            
            # Create the template
            template = CardTemplate(
                id=uuid.uuid4(),
                athlete_id=athlete.id,
                version=version,
                etrnl_url_group_id=template_id,
                template_code=sku,
                minted_count=0,
                edition_cap=None,
                image_url=f"/assets/cards/{sku}.png"  # Default image URL
            )
            
            db.session.add(template)
            print(f"  ✅ Created: {athlete.full_name} ({version}) - {template_id} ({sku})")
            created_count += 1
        
        db.session.commit()
        print(f"\n🎉 Successfully created {created_count} missing templates!")
        
        # Verify final count
        total_templates = CardTemplate.query.count()
        print(f"📊 Total templates in database: {total_templates}")


if __name__ == '__main__':
    create_missing_templates()
