# backend/routes_collection.py
from flask import Blueprint, jsonify, session
from models import db, CardInstance, CardTemplate, Athlete
from sqlalchemy.orm import joinedload
import uuid as uuidlib

bp = Blueprint('collection', __name__, url_prefix='/api/collection')

def _uuid(val):
    try: return uuidlib.UUID(str(val))
    except Exception: return None

@bp.get('')
def my_collection():
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
            }
        })

    return jsonify({'items': items})
