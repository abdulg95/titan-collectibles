#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Athlete, CardTemplate, AthleteAchievement, AthleteQualification
from sqlalchemy import text

def check_athletes():
    with app.app_context():
        athletes = Athlete.query.all()
        print(f'Total athletes: {len(athletes)}')
        print('=' * 80)
        
        for athlete in athletes:
            print(f'{athlete.full_name}:')
            print(f'  - card_number: {athlete.card_number}')
            print(f'  - card_image_url: {athlete.card_image_url}')
            print(f'  - sponsors: {bool(athlete.sponsors)} ({len(athlete.sponsors) if athlete.sponsors else 0} items)')
            print(f'  - socials: {bool(athlete.socials)} ({len(athlete.socials) if athlete.socials else 0} items)')
            print(f'  - achievements: {len(athlete.achievements)}')
            print(f'  - qualifications: {len(athlete.qualifications)}')
            
            # Check card templates
            templates = CardTemplate.query.filter_by(athlete_id=athlete.id).all()
            print(f'  - card_templates: {len(templates)}')
            for template in templates:
                print(f'    - {template.template_code}: image_url={template.image_url}')
            print()

if __name__ == '__main__':
    check_athletes()
