from app import app
from models import db, Athlete

BIO_SHORT = (
    "Born in Istanbul in 1999, Mete Gazoz was destined to be an archer. His father is a former "
    "national-level competitive archer, while his mother is the president of the Istanbul Archery Club. "
    "Becoming an archer in family immersed in the sport is one thing, but becoming a record-breaking bowman "
    "is something else, but since Mete first picked up a bow to begin practicing in 2010 he seems to have "
    "been on the fast-track to the very pinnacle of the sport."
)

BIO_LONG = (
    "Born in Istanbul in 1999, Mete Gazoz was destined to be an archer. His father is a former "
    "national-level competitive archer, while his mother is the president of the Istanbul Archery Club. "
    "Becoming an archer in family immersed in the sport is one thing, but becoming a record-breaking bowman "
    "is something else, but since Mete first picked up a bow to begin practicing in 2010 he seems to have "
    "been on the fast-track to the very pinnacle of the sport. The right-handed recurve bow shooter first "
    "dipped his toes into international competition in 2013, winning his first major medal that same year as "
    "part of the silver medal-winning Turkish team at the World Youth Archery Championship. A year later he "
    "claimed silver at the 2014 Youth Olympic Games in China, and just two years later he was representing "
    "Türkiye on the full Olympic stage in Rio 2016."
)

def main():
    with app.app_context():
        mete = Athlete.query.filter_by(full_name='Mete Gazoz').first()
        if mete is None:
            raise SystemExit('Mete Gazoz not found')
        mete.bio_short = BIO_SHORT
        mete.bio_long = BIO_LONG
        db.session.commit()
        print('Updated Mete Gazoz bio_short and bio_long')

if __name__ == '__main__':
    main()
