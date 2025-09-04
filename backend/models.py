from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, Enum, CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
import uuid, enum

db = SQLAlchemy()
migrate = Migrate()

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
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    picture = db.Column(db.String, nullable=True)

     # helpers
    def set_password(self, raw: str):
        # You can add your own policy checks before hashing (len, entropy, etc.)
        self.password_hash = generate_password_hash(raw, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, raw: str) -> bool:
        return bool(self.password_hash) and check_password_hash(self.password_hash, raw)

class Athlete(db.Model):
    __tablename__ = 'athletes'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date)
    sport = db.Column(db.String)
    nationality = db.Column(db.String)
    handedness = db.Column(db.String)
    world_ranking = db.Column(db.Integer)
    best_world_ranking = db.Column(db.Integer)
    intl_debut_year = db.Column(db.Integer)

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
    etrnl_url_group_id = db.Column(db.String)
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
