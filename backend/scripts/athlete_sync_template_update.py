# Add this to your existing sync_athletes.py script after the athlete sync section:

# Template mapping for new verification system
athlete_template_mapping = {
    'Brady Ellison': {'regular': '000000000001', 'diamond': '000000000002'},
    'Mete Gazoz': {'regular': '000000000003', 'diamond': '000000000004'},
    'Ella Gibson': {'regular': '000000000005', 'diamond': '000000000006'},
    'Deepika Kumari': {'regular': '000000000007', 'diamond': '000000000008'},
    'Sara López': {'regular': '000000000009', 'diamond': '000000000010'},
    'Mike Schloesser': {'regular': '000000000011', 'diamond': '000000000012'},
    'Lim Sihyeon': {'regular': '000000000013', 'diamond': '000000000014'},
    'Mathias Fullerton': {'regular': '000000000015', 'diamond': '000000000016'},
    'Kim Woojin': {'regular': '000000000017', 'diamond': '000000000018'}
}

# After athlete sync, add template creation/update:
print("\n🎯 Creating/updating card templates for new verification system...")

for athlete_data in athletes_data:
    name = athlete_data['full_name']
    slug = athlete_data['slug']
    
    # Get athlete ID
    cur.execute("SELECT id FROM athletes WHERE slug = %s", (slug,))
    athlete_result = cur.fetchone()
    if not athlete_result:
        continue
        
    athlete_id = athlete_result[0]
    
    # Create templates for both regular and diamond versions
    for version in ['regular', 'diamond']:
        template_code = athlete_template_mapping.get(name, {}).get(version)
        if not template_code:
            continue
            
        # Check if template already exists
        cur.execute("""
            SELECT id FROM card_templates 
            WHERE athlete_id = %s AND version = %s
        """, (athlete_id, version))
        
        existing_template = cur.fetchone()
        
        if existing_template:
            # Update existing template with new template_code
            cur.execute("""
                UPDATE card_templates 
                SET template_code = %s, updated_at = NOW()
                WHERE athlete_id = %s AND version = %s
            """, (template_code, athlete_id, version))
            print(f"🔄 Updated {name} {version} template with code {template_code}")
        else:
            # Create new template
            cur.execute("""
                INSERT INTO card_templates (
                    id, athlete_id, version, template_code, minted_count, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), %s, %s, %s, 0, NOW(), NOW()
                )
            """, (athlete_id, version, template_code))
            print(f"➕ Created {name} {version} template with code {template_code}")
