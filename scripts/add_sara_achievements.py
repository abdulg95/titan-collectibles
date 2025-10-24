import os
import sys
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, Athlete, AthleteAchievement

def create_app():
    app = Flask(__name__)
    if os.environ.get("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

def add_sara_achievements():
    app = create_app()
    with app.app_context():
        print("🏆 Adding Sara López's achievements to production database...")
        
        # Load athlete seed data
        seed_file_path = os.path.join(os.path.dirname(__file__), '../seeds/athlete_seed.json')
        with open(seed_file_path, 'r') as f:
            athletes_data = json.load(f)
        
        # Find Sara's data
        sara_data = None
        for athlete_data in athletes_data:
            if athlete_data['full_name'] == 'Sara López':
                sara_data = athlete_data
                break
        
        if not sara_data:
            print("❌ Sara López not found in seed data")
            return
        
        # Find Sara in database
        sara = Athlete.query.filter_by(full_name='Sara López').first()
        if not sara:
            print("❌ Sara López not found in database")
            return
        
        print(f"✅ Found Sara López in database (ID: {sara.id})")
        
        # Check if achievements already exist
        existing_achievements = AthleteAchievement.query.filter_by(athlete_id=sara.id).count()
        if existing_achievements > 0:
            print(f"⚠️  Sara already has {existing_achievements} achievements in database")
            return
        
        # Add achievements
        achievements_data = sara_data.get('achievements', [])
        added_count = 0
        
        for achievement_data in achievements_data:
            achievement = AthleteAchievement(
                athlete_id=sara.id,
                title=achievement_data.get('title'),
                result=achievement_data.get('result'),
                year=achievement_data.get('year'),
                notes=achievement_data.get('notes'),
                display_order=achievement_data.get('display_order', 0)
            )
            db.session.add(achievement)
            added_count += 1
            print(f"  ➕ Added: {achievement_data.get('title')}")
        
        db.session.commit()
        print(f"\n🎉 Successfully added {added_count} achievements for Sara López!")

if __name__ == "__main__":
    add_sara_achievements()
