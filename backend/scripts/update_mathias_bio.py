from app import app
from models import db, Athlete

BIO_LONG = (
    "Mathias Fullerton is a Danish compound archer who has rapidly risen to prominence in international competition. "
    "A standout since his cadet years, he captured team silver at the 2019 World Archery Youth Championships, then "
    "individual silver at the 2021 European Archery Championships in Antalya. In 2023, he claimed team gold at the "
    "World Archery Youth Championships and team silver at both the World Archery Championships and European Games. The "
    "following year, Fullerton triumphed at the prestigious Vegas Shoot, secured team gold at the European Indoor Archery "
    "Championships, and earned individual gold plus team bronze at the European Archery Championships in Essen. Known for "
    "his composure and precision under pressure, he continues shaping Denmark’s archery future."
)


def main():
    with app.app_context():
        mathias = Athlete.query.filter_by(full_name='Mathias Fullerton').first()
        if mathias is None:
            raise SystemExit('Mathias Fullerton not found')
        mathias.bio_long = BIO_LONG
        db.session.commit()
        print('Updated Mathias Fullerton bio_long')
        print('Preview:', repr(mathias.bio_long[:160]))


if __name__ == '__main__':
    main()
