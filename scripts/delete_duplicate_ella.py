#!/usr/bin/env python3

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Athlete, AthleteAchievement, AthleteQualification, CardTemplate

def delete_duplicate_ella():
    """Delete duplicate Ella Gibson record, keeping the one with updated video URL"""
    with app.app_context():
        # Find all Ella Gibson records
        ella_records = Athlete.query.filter_by(full_name='Ella Gibson').all()
        print(f"Found {len(ella_records)} Ella Gibson records")
        
        if len(ella_records) <= 1:
            print("No duplicates found")
            return
        
        # Identify which record to keep (the one with the new video URL)
        keep_record = None
        delete_records = []
        
        for record in ella_records:
            print(f"Record ID {record.id}: video_url = {record.video_url}")
            if record.video_url == "https://www.youtube.com/shorts/pZgSLCpL5rs":
                keep_record = record
                print(f"  -> KEEPING this record (has new video URL)")
            else:
                delete_records.append(record)
                print(f"  -> DELETING this record (has old video URL)")
        
        if not keep_record:
            print("ERROR: No record found with the new video URL!")
            return
        
        print(f"\nWill keep record ID {keep_record.id}")
        print(f"Will delete {len(delete_records)} duplicate record(s)")
        
        # Delete duplicate records
        for record in delete_records:
            print(f"\nDeleting duplicate record ID {record.id}...")
            
            # Delete related records first
            AthleteAchievement.query.filter_by(athlete_id=record.id).delete()
            AthleteQualification.query.filter_by(athlete_id=record.id).delete()
            CardTemplate.query.filter_by(athlete_id=record.id).delete()
            
            # Delete the athlete record
            db.session.delete(record)
            print(f"  Deleted athlete record ID {record.id}")
        
        db.session.commit()
        print(f"\n✅ Successfully deleted {len(delete_records)} duplicate Ella Gibson record(s)")
        
        # Verify the result
        remaining_records = Athlete.query.filter_by(full_name='Ella Gibson').all()
        print(f"\nRemaining Ella Gibson records: {len(remaining_records)}")
        for record in remaining_records:
            print(f"  Record ID {record.id}: video_url = {record.video_url}")

if __name__ == '__main__':
    delete_duplicate_ella()
