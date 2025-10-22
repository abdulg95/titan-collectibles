#!/usr/bin/env python3

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Athlete

def check_video_urls():
    """Check if athletes have video URLs loaded"""
    with app.app_context():
        athletes = Athlete.query.all()
        print(f'📊 Checking video URLs for {len(athletes)} athletes:')
        print('=' * 80)
        
        for athlete in athletes:
            print(f'{athlete.full_name}:')
            print(f'  - video_url: {athlete.video_url}')
            print(f'  - card_image_url: {athlete.card_image_url}')
            print(f'  - card_back_url: {athlete.card_back_url}')
            print(f'  - hero_image_url: {athlete.hero_image_url}')
            print(f'  - quote_photo_url: {athlete.quote_photo_url}')
            print(f'  - action_photo_url: {athlete.action_photo_url}')
            print()

if __name__ == '__main__':
    check_video_urls()
