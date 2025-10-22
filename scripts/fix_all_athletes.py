#!/usr/bin/env python3

import os
import sys
import json
import re
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Athlete, CardTemplate, AthleteAchievement, AthleteQualification

def generate_slug(name):
    """Generate a URL-friendly slug from a name"""
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def load_athlete_seed_data():
    """Load athlete data from the seed file"""
    seed_file = os.path.join(os.path.dirname(__file__), '..', 'seeds', 'athlete_seed.json')
    with open(seed_file, 'r') as f:
        return json.load(f)

def fix_all_athletes():
    """Fix all athletes with missing data"""
    with app.app_context():
        print("🔍 Loading athlete seed data...")
        seed_data = load_athlete_seed_data()
        
        print(f"📊 Found {len(seed_data)} athletes in seed data")
        
        # Get all existing athletes
        existing_athletes = Athlete.query.all()
        print(f"📊 Found {len(existing_athletes)} athletes in database")
        
        for seed_athlete in seed_data:
            full_name = seed_athlete.get('full_name')
            if not full_name:
                continue
                
            print(f"\n🔄 Processing: {full_name}")
            
            # Find existing athlete by name
            athlete = Athlete.query.filter_by(full_name=full_name).first()
            if not athlete:
                print(f"❌ Athlete {full_name} not found in database")
                continue
            
            # Generate slug if missing
            if not athlete.slug:
                base_slug = generate_slug(full_name)
                slug = base_slug
                counter = 1
                while Athlete.query.filter_by(slug=slug).filter(Athlete.id != athlete.id).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                athlete.slug = slug
                print(f"✅ Generated slug: {athlete.slug}")
            
            # Update sponsors
            if seed_athlete.get('sponsors'):
                athlete.sponsors = seed_athlete['sponsors']
                print(f"✅ Updated sponsors: {len(athlete.sponsors)} items")
            
            # Update socials
            if seed_athlete.get('socials'):
                athlete.socials = seed_athlete['socials']
                print(f"✅ Updated socials: {len(athlete.socials)} items")
            
            # Update card_image_url
            if seed_athlete.get('card_image_url'):
                athlete.card_image_url = seed_athlete['card_image_url']
                print(f"✅ Updated card_image_url: {athlete.card_image_url}")
            
            # Update other image URLs
            if seed_athlete.get('card_back_url'):
                athlete.card_back_url = seed_athlete['card_back_url']
                print(f"✅ Updated card_back_url: {athlete.card_back_url}")
            if seed_athlete.get('hero_image_url'):
                athlete.hero_image_url = seed_athlete['hero_image_url']
                print(f"✅ Updated hero_image_url: {athlete.hero_image_url}")
            if seed_athlete.get('video_url'):
                athlete.video_url = seed_athlete['video_url']
                print(f"✅ Updated video_url: {athlete.video_url}")
            if seed_athlete.get('quote_photo_url'):
                athlete.quote_photo_url = seed_athlete['quote_photo_url']
                print(f"✅ Updated quote_photo_url: {athlete.quote_photo_url}")
            if seed_athlete.get('action_photo_url'):
                athlete.action_photo_url = seed_athlete['action_photo_url']
                print(f"✅ Updated action_photo_url: {athlete.action_photo_url}")
            if seed_athlete.get('qualification_image_url'):
                athlete.qualification_image_url = seed_athlete['qualification_image_url']
                print(f"✅ Updated qualification_image_url: {athlete.qualification_image_url}")
            
            # Clear and reload achievements
            if seed_athlete.get('achievements'):
                # Clear existing achievements
                AthleteAchievement.query.filter_by(athlete_id=athlete.id).delete()
                
                # Add new achievements
                for achievement_data in seed_athlete['achievements']:
                    achievement = AthleteAchievement(
                        athlete_id=athlete.id,
                        title=achievement_data.get('title', ''),
                        year=achievement_data.get('year'),
                        result=achievement_data.get('result', ''),
                        notes=achievement_data.get('notes', ''),
                        medal=achievement_data.get('medal', 'none'),
                        position=achievement_data.get('position'),
                        display_order=achievement_data.get('display_order', 0)
                    )
                    db.session.add(achievement)
                
                print(f"✅ Updated achievements: {len(seed_athlete['achievements'])} items")
            
            # Clear and reload qualifications
            if seed_athlete.get('qualifications'):
                # Clear existing qualifications
                AthleteQualification.query.filter_by(athlete_id=athlete.id).delete()
                
                # Add new qualifications
                for qual_data in seed_athlete['qualifications']:
                    qualification = AthleteQualification(
                        athlete_id=athlete.id,
                        year=qual_data.get('year'),
                        score=qual_data.get('score'),
                        event=qual_data.get('event', '')
                    )
                    db.session.add(qualification)
                
                print(f"✅ Updated qualifications: {len(seed_athlete['qualifications'])} items")
            
            # Update card templates
            templates = CardTemplate.query.filter_by(athlete_id=athlete.id).all()
            for template in templates:
                if template.template_code == 'diamond':
                    template.image_url = seed_athlete.get('card_image_url', '').replace('-REG.png', '-DIA.png')
                else:
                    template.image_url = seed_athlete.get('card_image_url', '')
                print(f"✅ Updated template {template.template_code}: {template.image_url}")
        
        # Commit all changes
        db.session.commit()
        print(f"\n🎉 Successfully updated all athletes!")

if __name__ == '__main__':
    fix_all_athletes()
