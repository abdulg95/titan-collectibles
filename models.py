from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy import func, Enum, CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import uuid, enum

db = SQLAlchemy()
migrate = Migrate()

# --- Postgres ENUM types for stored string enums ---
ArcheryDiscipline = ENUM(
    'compound', 'recurve', 'barebow', 'other',
    name='archery_discipline',
    create_type=True,
)
Handedness = ENUM(
    'left', 'right', 'ambidextrous',
    name='handedness',
    create_type=True,
)
Medal = ENUM(
    'gold', 'silver', 'bronze', 'none',
    name='medal',
    create_type=True,
)

# --- Python Enum wrapped with SQLAlchemy Enum for app status ---
class CardStatus(enum.Enum):
    unassigned = "unassigned"
    shipped = "shipped"
    claimed = "claimed"


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String, nullable=True)  # allow Google-only users
    email = db.Column(db.String, unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    google_sub = db.Column(db.String, unique=True, index=True, nullable=True)
    picture = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(),
                           onupdate=func.now())

    # helpers
    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(
            raw, method='pbkdf2:sha256', salt_length=16
        )

    def check_password(self, raw: str) -> bool:
        return bool(self.password_hash) and check_password_hash(self.password_hash, raw)


class Athlete(db.Model):
    __tablename__ = 'athletes'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity / routing
    full_name = db.Column(db.String, nullable=False, index=True)
    slug = db.Column(db.String, unique=True, index=True)      # e.g., "mathias-fullerton"
    
    # Series information
    series_number = db.Column(db.Integer, nullable=False, default=1)  # Series 1, 2, 3, etc.
    card_number = db.Column(db.Integer, unique=True, index=True)       # 001, 002, 003, etc.

    # About
    dob = db.Column(db.Date)                                   # birth date
    nationality = db.Column(db.String)                         # e.g., "Denmark"
    hometown = db.Column(db.String)                            # optional
    sport = db.Column(db.String, default='Archery')
    discipline = db.Column(ArcheryDiscipline, nullable=True)   # compound/recurve/...
    handedness = db.Column(Handedness, nullable=True)

    world_ranking = db.Column(db.Integer)                      # current
    best_world_ranking = db.Column(db.Integer)
    intl_debut_year = db.Column(db.Integer)                    # career start

    # Profile content
    bio_short = db.Column(db.Text)                             # preview/1st paragraph
    bio_long = db.Column(db.Text)                              # full bio (expanded)
    quote_text = db.Column(db.Text)                            # “Mostly what’s changed…”
    quote_source = db.Column(db.String)                        # optional attribution

    # Media used on the page
    card_image_url = db.Column(db.Text)                        # trading card image (front)
    card_back_url = db.Column(db.Text)                         # trading card back image
    hero_image_url = db.Column(db.Text)                        # top banner image
    video_url = db.Column(db.Text)                             # interview/highlight video
    quote_photo_url = db.Column(db.Text)                       # background photo for quote section
    action_photo_url = db.Column(db.Text)                       # action photo after career statistics
    qualification_image_url = db.Column(db.Text)                # best qualification graph image
    gallery = db.Column(JSONB, default=list)                   # [{url,alt,caption,order}, …]

    # Links / social / sponsors
    socials = db.Column(JSONB, default=dict)                   # {instagram, youtube, tiktok, ...}
    sponsors = db.Column(JSONB, default=list)                  # [{name, logo_url, url}, …]

    # Timestamps (timezone-aware)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Relationships
    achievements = db.relationship(
        'AthleteAchievement', backref='athlete',
        cascade='all, delete-orphan',
        order_by='AthleteAchievement.display_order'
    )
    equipment = db.relationship(
        'AthleteEquipment', backref='athlete',
        cascade='all, delete-orphan',
        order_by='AthleteEquipment.display_order'
    )
    stats = db.relationship(
        'AthleteStats', uselist=False, backref='athlete',
        cascade='all, delete-orphan'
    )  # single row of aggregates
    qualifications = db.relationship(
        'AthleteQualification', backref='athlete',
        cascade='all, delete-orphan',
        order_by='AthleteQualification.year'
    )

    # convenience (computed age)
    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - (
            (today.month, today.day) < (self.dob.month, self.dob.day)
        )


class AthleteAchievement(db.Model):
    """For the 'Top achievements' list."""
    __tablename__ = 'athlete_achievements'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = db.Column(UUID(as_uuid=True), db.ForeignKey('athletes.id'), nullable=False)

    title = db.Column(db.String, nullable=False)               # e.g., "World Archery Championships"
    year = db.Column(db.Integer)                               # optional (multi-year possible)
    result = db.Column(db.String)                              # "Multi-time medalist", "Champion (2024)"
    medal = db.Column(Medal, default='none')                   # icon hint
    position = db.Column(db.Integer)                           # 1 = champion, etc. (optional)
    notes = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)


class AthleteEquipment(db.Model):
    """For the 'Equipment' two-column list."""
    __tablename__ = 'athlete_equipment'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = db.Column(UUID(as_uuid=True), db.ForeignKey('athletes.id'), nullable=False)

    category = db.Column(db.String, nullable=False)            # "Bow", "Sight", "Arrows", "Release", ...
    brand = db.Column(db.String)
    model = db.Column(db.String)
    url = db.Column(db.Text)                                   # product link if available
    notes = db.Column(db.String)                               # spec details
    display_order = db.Column(db.Integer, default=0)


class AthleteStats(db.Model):
    """Aggregates shown under 'Career statistics'."""
    __tablename__ = 'athlete_stats'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = db.Column(UUID(as_uuid=True), db.ForeignKey('athletes.id'), nullable=False, unique=True)

    win_percentage = db.Column(db.Numeric(5, 2))               # e.g., 72.00
    average_arrow = db.Column(db.Numeric(4, 2))                 # e.g., 9.82
    tiebreak_win_rate = db.Column(db.Numeric(5, 2))             # e.g., 35.00
    extras = db.Column(JSONB, default=dict)                     # room for more KPIs later


class AthleteQualification(db.Model):
    """Time-series for the 'Best qualification' graph (per year)."""
    __tablename__ = 'athlete_qualifications'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = db.Column(UUID(as_uuid=True), db.ForeignKey('athletes.id'), nullable=False)

    year = db.Column(db.Integer, nullable=False)               # 2021, 2022, …
    score = db.Column(db.Numeric(6, 2), nullable=False)        # e.g., 710.0 (72-arrow 720 round)
    event = db.Column(db.String)


# models.py  (CardTemplate)
class CardTemplate(db.Model):
    __tablename__ = 'card_templates'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = db.Column(UUID(as_uuid=True), db.ForeignKey('athletes.id'), nullable=False)
    version = db.Column(db.String, nullable=False)  # 'regular' | 'diamond'
    product_id = db.Column(UUID(as_uuid=True))
    variant_id = db.Column(UUID(as_uuid=True))
    edition_cap = db.Column(db.Integer)
    minted_count = db.Column(db.Integer, nullable=False, default=0)
    glb_url = db.Column(db.String)
    image_url = db.Column(db.String)

    # NEW: your spreadsheet’s short code, e.g. 000000000018
    template_code = db.Column(db.String, index=True)   # <— add this

    # Keep this strictly for the actual ETRNL group id returned by their API
    etrnl_url_group_id = db.Column(db.String)
    athlete = db.relationship('Athlete', backref=db.backref('templates', lazy='dynamic'))

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    __table_args__ = (CheckConstraint("version in ('regular','diamond')", name='ck_template_version'),)



class CardInstance(db.Model):
    __tablename__ = 'card_instances'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = db.Column(UUID(as_uuid=True), db.ForeignKey('card_templates.id'), nullable=False)
    serial_no = db.Column(db.Integer, nullable=False)
    etrnl_tag_uid = db.Column(db.String, unique=True, index=True)
    etrnl_tag_id = db.Column(db.String, unique=True, index=True)
    last_ctr = db.Column(db.Integer, nullable=False, default=0)
    tamper_status = db.Column(db.String)
    owner_user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    status = db.Column(Enum(CardStatus), nullable=False, default=CardStatus.unassigned)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # NEW: ORM relationships
    template = db.relationship('CardTemplate', backref=db.backref('instances', lazy='dynamic'))
    owner = db.relationship('User', backref='card_instances', foreign_keys=[owner_user_id])


class ScanEvent(db.Model):
    __tablename__ = 'scans'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_instance_id = db.Column(UUID(as_uuid=True), db.ForeignKey('card_instances.id'))
    tag_id = db.Column(db.String)
    uid = db.Column(db.String)
    ctr = db.Column(db.Integer)
    authentic = db.Column(db.Boolean)
    tt_curr = db.Column(db.String)
    tt_perm = db.Column(db.String)
    ip = db.Column(db.String)
    user_agent = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
