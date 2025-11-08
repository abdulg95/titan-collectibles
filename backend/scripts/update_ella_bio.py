from app import app
from models import db, Athlete

BIO_LONG = (
    "Ella Gibson is a British international compound archer who has become one of the sport’s most dominant figures. "
    "A World Games, European Outdoor, and Indoor champion, she made her senior debut in 2019 after winning mixed team "
    "bronze at the World Archery Youth Championships. Her breakthrough came in 2021 with individual silver at the "
    "European Championships in Türkiye.\n\nThe following year she captured her first major title at the European Indoor "
    "Championships, swept all three Hyundai Archery World Cup stages she entered, and claimed World Games gold in "
    "Alabama. Her success carried into 2023 with silver at the European Games and two bronzes at the World Archery Field "
    "Championships. In 2024 she was crowned European Champion in Essen, Germany. By 2025, Gibson had celebrated an "
    "extraordinary 1,000 days ranked as the world number one."
)


def main():
    with app.app_context():
        ella = Athlete.query.filter_by(full_name='Ella Gibson').first()
        if ella is None:
            raise SystemExit('Ella Gibson not found')
        ella.bio_long = BIO_LONG
        db.session.commit()
        print('Updated Ella Gibson bio_long')
        print('Preview:', repr(ella.bio_long[:160]))


if __name__ == '__main__':
    main()
