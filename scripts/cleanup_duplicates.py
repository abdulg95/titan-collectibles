#!/usr/bin/env python3

import os
import sys
from collections import defaultdict

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Athlete, AthleteAchievement, AthleteQualification, CardTemplate

def find_and_delete_duplicates():
    """Find and delete duplicate athlete records"""
    with app.app_context():
        # Get all athletes
        all_athletes = Athlete.query.all()
        print(f"📊 Total athletes in database: {len(all_athletes)}")
        
        # Group athletes by full_name
        athletes_by_name = defaultdict(list)
        for athlete in all_athletes:
            athletes_by_name[athlete.full_name].append(athlete)
        
        # Find duplicates
        duplicates_found = False
        total_deleted = 0
        
        for name, athletes in athletes_by_name.items():
            if len(athletes) > 1:
                duplicates_found = True
                print(f"\n🔍 Found {len(athletes)} duplicate records for: {name}")
                
                # Sort by creation/update criteria to determine which to keep
                # Priority: 1) Has card_number, 2) Has more complete data, 3) Has newer video URLs
                def sort_key(athlete):
                    score = 0
                    if athlete.card_number:
                        score += 1000
                    if athlete.video_url and 'shorts' in athlete.video_url:
                        score += 100  # Prefer shorts over regular videos
                    if athlete.sponsors and len(athlete.sponsors) > 0:
                        score += 50
                    if athlete.socials and len(athlete.socials) > 0:
                        score += 50
                    if athlete.card_image_url:
                        score += 25
                    return score
                
                athletes.sort(key=sort_key, reverse=True)
                
                # Keep the first (highest priority) record
                keep_record = athletes[0]
                delete_records = athletes[1:]
                
                print(f"  ✅ KEEPING: ID {keep_record.id}")
                print(f"    - card_number: {keep_record.card_number}")
                print(f"    - video_url: {keep_record.video_url}")
                print(f"    - sponsors: {len(keep_record.sponsors) if keep_record.sponsors else 0}")
                print(f"    - socials: {len(keep_record.socials) if keep_record.socials else 0}")
                
                # Delete duplicate records
                for record in delete_records:
                    print(f"  ❌ DELETING: ID {record.id}")
                    print(f"    - card_number: {record.card_number}")
                    print(f"    - video_url: {record.video_url}")
                    print(f"    - sponsors: {len(record.sponsors) if record.sponsors else 0}")
                    print(f"    - socials: {len(record.socials) if record.socials else 0}")
                    
                    # Delete related records first
                    AthleteAchievement.query.filter_by(athlete_id=record.id).delete()
                    AthleteQualification.query.filter_by(athlete_id=record.id).delete()
                    CardTemplate.query.filter_by(athlete_id=record.id).delete()
                    
                    # Delete the athlete record
                    db.session.delete(record)
                    total_deleted += 1
        
        if not duplicates_found:
            print("✅ No duplicate athlete records found!")
            return
        
        # Commit changes
        db.session.commit()
        print(f"\n🎉 Successfully deleted {total_deleted} duplicate athlete record(s)")
        
        # Verify the result
        remaining_athletes = Athlete.query.all()
        print(f"\n📊 Remaining athletes: {len(remaining_athletes)}")
        
        # Show final count by name
        final_count = defaultdict(int)
        for athlete in remaining_athletes:
            final_count[athlete.full_name] += 1
        
        print("\n📋 Final athlete count:")
        for name, count in sorted(final_count.items()):
            if count > 1:
                print(f"  ⚠️  {name}: {count} records (still has duplicates!)")
            else:
                print(f"  ✅ {name}: {count} record")

if __name__ == '__main__':
    find_and_delete_duplicates()
