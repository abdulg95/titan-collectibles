# backend/routes_collection.py
from flask import Blueprint, jsonify, session, request
from models import db, CardInstance, CardTemplate, Athlete, User
from sqlalchemy.orm import joinedload
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
import uuid as uuidlib

bp = Blueprint('collection', __name__, url_prefix='/api/collection')

def _uuid(val):
    try: return uuidlib.UUID(str(val))
    except Exception: return None

def _verify_auth_token(token):
    """Verify and extract user ID from auth token"""
    try:
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        user_id = serializer.loads(token, salt=current_app.config.get('AUTH_TOKEN_SALT', 'auth-token'), max_age=3600)  # 1 hour expiry
        return user_id
    except (BadSignature, SignatureExpired):
        return None

@bp.get('')
def my_collection():
    # Try auth token from query parameter first (for Safari mobile compatibility)
    auth_token = request.args.get('auth_token')
    uid = None
    
    if auth_token:
        user_id = _verify_auth_token(auth_token)
        if user_id:
            uid = _uuid(user_id)
    
    # Fallback to session-based authentication
    if not uid:
        uid = _uuid(session.get('uid'))
    
    if not uid:
        return jsonify({'error':'unauthorized'}), 401

    rows = (
        db.session.query(CardInstance)
        .options(
            joinedload(CardInstance.template),
            joinedload(CardInstance.template).joinedload(CardTemplate.athlete),
            # if you have a direct relationship, adjust accordingly
        )
        .join(CardTemplate, CardTemplate.id == CardInstance.template_id)
        .join(Athlete, Athlete.id == CardTemplate.athlete_id)
        .filter(CardInstance.owner_user_id == uid)
        .order_by(CardInstance.created_at.desc())
        .all()
    )

    items = []
    for ci in rows:
        tmpl = ci.template
        ath = tmpl.athlete if tmpl else None
        items.append({
            'id': str(ci.id),
            'serial_no': ci.serial_no,
            'status': ci.status.value if hasattr(ci.status, 'value') else str(ci.status),
            'template': {
                'version': getattr(tmpl, 'version', None),
                'image_url': getattr(tmpl, 'image_url', None),
                'glb_url': getattr(tmpl, 'glb_url', None),
            },
            'athlete': {
                'id': str(getattr(ath, 'id', '')),
                'full_name': getattr(ath, 'full_name', ''),
                'slug': getattr(ath, 'slug', ''),
                'card_image_url': getattr(ath, 'card_image_url', None),
                'card_number': getattr(ath, 'card_number', None),
                'series_number': getattr(ath, 'series_number', None),
            }
        })

    return jsonify({'items': items})
