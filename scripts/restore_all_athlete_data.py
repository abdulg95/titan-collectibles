#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Athlete, AthleteAchievement, AthleteEquipment, AthleteStats, AthleteQualification

def restore_athlete_data():
    with app.app_context():
        print("🔄 Restoring all athlete data...")
        
        # Restore Mathias Fullerton
        mathias = Athlete.query.filter_by(full_name='Mathias Fullerton').first()
        if mathias:
            print(f"\n📊 Restoring Mathias Fullerton...")
            
            # Socials
            mathias.socials = {
                'instagram': 'https://www.instagram.com/mathiasfullerton/',
                'facebook': 'https://www.facebook.com/Fnullerton/',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            mathias.sponsors = [
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'TruBall', 'logo_url': '/assets/sponsors/truball.png', 'url': 'https://truball.com'},
                {'name': 'Beiter', 'logo_url': '/assets/sponsors/beiter.png', 'url': 'https://beiter.com'},
                {'name': 'PSE', 'logo_url': '/assets/sponsors/pse.png', 'url': 'https://psearchery.com'},
                {'name': 'AAE', 'logo_url': '/assets/sponsors/aae.png', 'url': 'https://aae.com'},
                {'name': 'Axcel', 'logo_url': '/assets/sponsors/axcel.png', 'url': 'https://axcel.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=mathias.id).delete()
            achievements_data = [
                {'title': 'World Archery Championships', 'result': 'Multi-time medallist', 'medal': 'gold', 'notes': 'gold,silver,bronze', 'display_order': 0},
                {'title': 'European Championships', 'result': 'European Champion and silver medallist', 'medal': 'gold', 'notes': 'gold,silver', 'display_order': 1},
                {'title': 'World Cup Final', 'result': 'World Cup Final medallist', 'medal': 'gold', 'notes': 'gold', 'display_order': 2},
                {'title': 'World Cup Stages', 'result': 'Multiple stage medallist', 'medal': 'gold', 'notes': 'gold,gold', 'display_order': 3},
                {'title': 'The Vegas Shoot', 'result': 'Vegas Shoot Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 4}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=mathias.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(mathias.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Mete Gazoz
        mete = Athlete.query.filter_by(full_name='Mete Gazoz').first()
        if mete:
            print(f"\n📊 Restoring Mete Gazoz...")
            
            # Socials
            mete.socials = {
                'instagram': 'https://www.instagram.com/metegazoz',
                'facebook': '',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            mete.sponsors = [
                {'name': 'Shibuya', 'logo_url': '/assets/sponsors/shibuya.png', 'url': 'https://shibuya-archery.com'},
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'Nike', 'logo_url': '/assets/sponsors/nike.png', 'url': 'https://nike.com'},
                {'name': 'Red Bull', 'logo_url': '/assets/sponsors/redbull.png', 'url': 'https://redbull.com'},
                {'name': 'Vestel', 'logo_url': '/assets/sponsors/vestel.png', 'url': 'https://vestel.com'},
                {'name': 'Allianz', 'logo_url': '/assets/sponsors/allianz.png', 'url': 'https://allianz.com'},
                {'name': 'Ramrodz', 'logo_url': '/assets/sponsors/ramrodz.png', 'url': 'https://ramrodz.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=mete.id).delete()
            achievements_data = [
                {'title': 'Olympic Games', 'result': 'Olympic Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 0},
                {'title': 'World Archery Championships', 'result': 'World Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 1},
                {'title': 'European Championships', 'result': 'European Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 2},
                {'title': 'World Cup Final', 'result': 'World Cup Final Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=mete.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(mete.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Lim Sihyeon
        lim = Athlete.query.filter_by(full_name='Lim Sihyeon').first()
        if lim:
            print(f"\n📊 Restoring Lim Sihyeon...")
            
            # Socials
            lim.socials = {
                'instagram': 'https://www.instagram.com/limsihyeon',
                'facebook': '',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            lim.sponsors = [
                {'name': 'Shibuya', 'logo_url': '/assets/sponsors/shibuya.png', 'url': 'https://shibuya-archery.com'},
                {'name': 'Wiawis', 'logo_url': '/assets/sponsors/wiawis.png', 'url': 'https://wiawis.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=lim.id).delete()
            achievements_data = [
                {'title': 'Olympic Games', 'result': 'Triple Olympic Champion', 'medal': 'gold', 'notes': 'gold,gold,gold', 'display_order': 0},
                {'title': 'Asian Games', 'result': 'Triple Asian Games Champion', 'medal': 'gold', 'notes': 'gold,gold,gold', 'display_order': 1},
                {'title': 'World Cup', 'result': 'World Cup Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 2},
                {'title': 'Asian Championships', 'result': 'Asian Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=lim.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(lim.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Kim Woojin
        kim = Athlete.query.filter_by(full_name='Kim Woojin').first()
        if kim:
            print(f"\n📊 Restoring Kim Woojin...")
            
            # Socials
            kim.socials = {
                'instagram': 'https://www.instagram.com/kimwoojin',
                'facebook': '',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            kim.sponsors = [
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'TruBall', 'logo_url': '/assets/sponsors/truball.png', 'url': 'https://truball.com'},
                {'name': 'Beiter', 'logo_url': '/assets/sponsors/beiter.png', 'url': 'https://beiter.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=kim.id).delete()
            achievements_data = [
                {'title': 'Olympic Games', 'result': '5x Olympic Champion', 'medal': 'gold', 'notes': 'gold,gold,gold,gold,gold', 'display_order': 0},
                {'title': 'World Archery Championships', 'result': '3x World Champion', 'medal': 'gold', 'notes': 'gold,gold,gold', 'display_order': 1},
                {'title': 'World Cup Final', 'result': '5x World Cup Final Champion', 'medal': 'gold', 'notes': 'gold,gold,gold,gold,gold', 'display_order': 2},
                {'title': 'Asian Games', 'result': '2x Asian Games Champion', 'medal': 'gold', 'notes': 'gold,gold', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=kim.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(kim.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Ella Gibson
        ella = Athlete.query.filter_by(full_name='Ella Gibson').first()
        if ella:
            print(f"\n📊 Restoring Ella Gibson...")
            
            # Socials
            ella.socials = {
                'instagram': 'https://www.instagram.com/ellagibson',
                'facebook': '',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            ella.sponsors = [
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'TruBall', 'logo_url': '/assets/sponsors/truball.png', 'url': 'https://truball.com'},
                {'name': 'Beiter', 'logo_url': '/assets/sponsors/beiter.png', 'url': 'https://beiter.com'},
                {'name': 'PSE', 'logo_url': '/assets/sponsors/pse.png', 'url': 'https://psearchery.com'},
                {'name': 'AAE', 'logo_url': '/assets/sponsors/aae.png', 'url': 'https://aae.com'},
                {'name': 'Axcel', 'logo_url': '/assets/sponsors/axcel.png', 'url': 'https://axcel.com'},
                {'name': 'MT', 'logo_url': '/assets/sponsors/mt.png', 'url': 'https://mt.com'},
                {'name': 'Feather Vision', 'logo_url': '/assets/sponsors/feather-vision.png', 'url': 'https://feathervision.com'},
                {'name': 'Dolcetti', 'logo_url': '/assets/sponsors/dolcetti.png', 'url': 'https://dolcetti.com'},
                {'name': 'Beiter', 'logo_url': '/assets/sponsors/beiter.png', 'url': 'https://beiter.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=ella.id).delete()
            achievements_data = [
                {'title': 'World Archery Championships', 'result': 'World Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 0},
                {'title': 'European Championships', 'result': 'European Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 1},
                {'title': 'World Cup Final', 'result': 'World Cup Final Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 2},
                {'title': 'World Games', 'result': 'World Games Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=ella.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(ella.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Deepika Kumari
        deepika = Athlete.query.filter_by(full_name='Deepika Kumari').first()
        if deepika:
            print(f"\n📊 Restoring Deepika Kumari...")
            
            # Socials
            deepika.socials = {
                'instagram': 'https://www.instagram.com/dkumari.archer/?hl=en',
                'facebook': 'https://www.facebook.com/DeepikaArchery/',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            deepika.sponsors = [
                {'name': 'Ramrodz', 'logo_url': '/assets/sponsors/ramrodz.png', 'url': 'https://ramrodz.com'},
                {'name': 'Beiter', 'logo_url': '/assets/sponsors/beiter.png', 'url': 'https://beiter.com'},
                {'name': 'Shibuya', 'logo_url': '/assets/sponsors/shibuya.png', 'url': 'https://shibuya-archery.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=deepika.id).delete()
            achievements_data = [
                {'title': 'Olympic Games', 'result': '4 appearances', 'medal': 'none', 'notes': '', 'display_order': 0},
                {'title': 'World Archery Championships', 'result': '2x Silver medallist', 'medal': 'silver', 'notes': 'silver,silver', 'display_order': 1},
                {'title': 'World Cup Final', 'result': '5x Silver medallist', 'medal': 'silver', 'notes': 'silver,silver,silver,silver,silver', 'display_order': 2},
                {'title': 'Asian Games', 'result': 'Team Bronze medallist', 'medal': 'bronze', 'notes': 'bronze', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=deepika.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(deepika.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Sara López
        sara = Athlete.query.filter_by(full_name='Sara López').first()
        if sara:
            print(f"\n📊 Restoring Sara López...")
            
            # Socials
            sara.socials = {
                'instagram': '',
                'facebook': '',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            sara.sponsors = [
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'TruBall', 'logo_url': '/assets/sponsors/truball.png', 'url': 'https://truball.com'},
                {'name': 'B-Stinger', 'logo_url': '/assets/sponsors/b-stinger.png', 'url': 'https://b-stinger.com'},
                {'name': 'Gas', 'logo_url': '/assets/sponsors/gas.png', 'url': 'https://gas.com'},
                {'name': 'Beiter', 'logo_url': '/assets/sponsors/beiter.png', 'url': 'https://beiter.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=sara.id).delete()
            achievements_data = [
                {'title': 'World Archery Championships', 'result': 'World Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 0},
                {'title': 'World Cup Final', 'result': '9x World Cup Final Champion', 'medal': 'gold', 'notes': 'gold,gold,gold,gold,gold,gold,gold,gold,gold', 'display_order': 1},
                {'title': 'Pan American Games', 'result': 'Pan American Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 2},
                {'title': 'World Games', 'result': 'World Games Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=sara.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(sara.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Restore Mike Schloesser
        mike = Athlete.query.filter_by(full_name='Mike Schloesser').first()
        if mike:
            print(f"\n📊 Restoring Mike Schloesser...")
            
            # Socials
            mike.socials = {
                'instagram': '',
                'facebook': '',
                'youtube': '',
                'tiktok': '',
                'x': ''
            }
            
            # Sponsors
            mike.sponsors = [
                {'name': 'Hoyt', 'logo_url': '/assets/sponsors/hoyt.png', 'url': 'https://hoyt.com'},
                {'name': 'Easton', 'logo_url': '/assets/sponsors/easton.png', 'url': 'https://eastonarchery.com'},
                {'name': 'TruBall', 'logo_url': '/assets/sponsors/truball.png', 'url': 'https://truball.com'},
                {'name': 'Gas', 'logo_url': '/assets/sponsors/gas.png', 'url': 'https://gas.com'}
            ]
            
            # Clear existing achievements and add new ones
            AthleteAchievement.query.filter_by(athlete_id=mike.id).delete()
            achievements_data = [
                {'title': 'World Archery Championships', 'result': '4x World Champion', 'medal': 'gold', 'notes': 'gold,gold,gold,gold', 'display_order': 0},
                {'title': 'World Cup Final', 'result': '4x World Cup Final Champion', 'medal': 'gold', 'notes': 'gold,gold,gold,gold', 'display_order': 1},
                {'title': 'European Championships', 'result': '6x European Champion', 'medal': 'gold', 'notes': 'gold,gold,gold,gold,gold,gold', 'display_order': 2},
                {'title': 'European Games', 'result': 'European Games Champion', 'medal': 'gold', 'notes': 'gold', 'display_order': 3}
            ]
            
            for ach_data in achievements_data:
                achievement = AthleteAchievement(
                    athlete_id=mike.id,
                    title=ach_data['title'],
                    result=ach_data['result'],
                    medal=ach_data['medal'],
                    notes=ach_data['notes'],
                    display_order=ach_data['display_order']
                )
                db.session.add(achievement)
            
            print(f"   ✅ Restored {len(achievements_data)} achievements")
            print(f"   ✅ Restored {len(mike.sponsors)} sponsors")
            print(f"   ✅ Restored social media links")
        
        # Commit all changes
        db.session.commit()
        print(f"\n🎯 All athlete data restored successfully!")
        print(f"✅ Database updated with complete achievements, sponsors, and social media data")

if __name__ == '__main__':
    restore_athlete_data()
