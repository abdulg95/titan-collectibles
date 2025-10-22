#!/usr/bin/env python3
"""
Check which card templates are missing from the database compared to templates.csv
"""

import csv
from app import app, db
from models import CardTemplate, Athlete
from sqlalchemy.orm import joinedload


def check_missing_templates():
    """Check which templates from templates.csv are missing in the database"""
    with app.app_context():
        print("🔍 Checking Card Templates:")
        
        # Read templates.csv
        templates_file_path = 'templates.csv'
        expected_templates = []
        
        with open(templates_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                expected_templates.append({
                    'template_id': row['template_id'],
                    'display_name': row['display_name'],
                    'version': row['version'],
                    'sku': row['sku']
                })
        
        print(f"📊 Expected templates from CSV: {len(expected_templates)}")
        
        # Get actual templates from database
        actual_templates = CardTemplate.query.join(Athlete).options(joinedload(CardTemplate.athlete)).all()
        print(f"📊 Actual templates in database: {len(actual_templates)}")
        
        # Check which ones are missing
        missing_templates = []
        found_templates = []
        
        for expected in expected_templates:
            # Try to find by template_code (etrnl_url_group_id)
            found = None
            for actual in actual_templates:
                if actual.etrnl_url_group_id == expected['template_id']:
                    found = actual
                    break
            
            if found:
                found_templates.append(expected)
                print(f"  ✅ {expected['display_name']} ({expected['version']}) - {expected['template_id']}")
            else:
                missing_templates.append(expected)
                print(f"  ❌ MISSING: {expected['display_name']} ({expected['version']}) - {expected['template_id']}")
        
        print(f"\n📋 Summary:")
        print(f"  ✅ Found: {len(found_templates)}")
        print(f"  ❌ Missing: {len(missing_templates)}")
        
        if missing_templates:
            print(f"\n🚨 Missing Templates:")
            for missing in missing_templates:
                print(f"  - {missing['display_name']} ({missing['version']}) - ID: {missing['template_id']} - SKU: {missing['sku']}")
        
        # Also check for any extra templates in database that aren't in CSV
        extra_templates = []
        for actual in actual_templates:
            found_in_csv = False
            for expected in expected_templates:
                if actual.etrnl_url_group_id == expected['template_id']:
                    found_in_csv = True
                    break
            
            if not found_in_csv:
                extra_templates.append(actual)
        
        if extra_templates:
            print(f"\n➕ Extra Templates in Database (not in CSV):")
            for extra in extra_templates:
                athlete_name = extra.athlete.full_name if extra.athlete else "Unknown"
                print(f"  - {athlete_name} ({extra.version}) - ID: {extra.etrnl_url_group_id} - Template ID: {extra.id}")


if __name__ == '__main__':
    check_missing_templates()
