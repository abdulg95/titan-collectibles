from models import db, Athlete, CardTemplate
from app import app

ATHLETES = [
  {"full_name":"Ellie Goulding","sport":"Track","nationality":"Canada"},
  {"full_name":"Athlete 2","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 3","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 4","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 5","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 6","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 7","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 8","sport":"Sport","nationality":"Country"},
  {"full_name":"Athlete 9","sport":"Sport","nationality":"Country"},
]

with app.app_context():
  for a in ATHLETES:
    ath = Athlete(full_name=a['full_name'], sport=a['sport'], nationality=a['nationality'])
    db.session.add(ath)
    db.session.flush()
    for v in ('regular','diamond'):
      tpl = CardTemplate(athlete_id=ath.id, version=v, glb_url='https://example.com/model.glb')
      db.session.add(tpl)
  db.session.commit()
  print('Seeded athletes + templates')
