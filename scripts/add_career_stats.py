import os
import sys
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, Athlete, AthleteStats

def create_app():
    app = Flask(__name__)
    if os.environ.get("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app

def add_career_stats():
    app = create_app()
    with app.app_context():
        print("📊 Adding career stats for all athletes...")
        
        # Load athlete seed data
        seed_file_path = os.path.join(os.path.dirname(__file__), '../seeds/athlete_seed.json')
        with open(seed_file_path, 'r') as f:
            athletes_data = json.load(f)
        
        updated_count = 0
        
        for athlete_data in athletes_data:
            full_name = athlete_data['full_name']
            stats_data = athlete_data.get('stats', {})
            
            if not stats_data:
                print(f"  ⚠️  No stats data found for {full_name}")
                continue
            
            # Find athlete in database
            athlete = Athlete.query.filter_by(full_name=full_name).first()
            if not athlete:
                print(f"  ❌ Athlete {full_name} not found in database")
                continue
            
            # Check if stats already exist
            existing_stats = AthleteStats.query.filter_by(athlete_id=athlete.id).first()
            
            if existing_stats:
                print(f"  ✅ {full_name}: Stats already exist, updating...")
                # Update existing stats
                existing_stats.win_percentage = stats_data.get('win_percentage')
                existing_stats.average_arrow = stats_data.get('average_arrow')
                existing_stats.tiebreak_win_rate = stats_data.get('tiebreak_win_rate')
                existing_stats.extras = stats_data.get('extras', {})
            else:
                print(f"  ➕ {full_name}: Creating new stats...")
                # Create new stats
                new_stats = AthleteStats(
                    athlete_id=athlete.id,
                    win_percentage=stats_data.get('win_percentage'),
                    average_arrow=stats_data.get('average_arrow'),
                    tiebreak_win_rate=stats_data.get('tiebreak_win_rate'),
                    extras=stats_data.get('extras', {})
                )
                db.session.add(new_stats)
            
            updated_count += 1
        
        db.session.commit()
        print(f"\n🎉 Successfully processed career stats for {updated_count} athletes!")

if __name__ == "__main__":
    add_career_stats()
