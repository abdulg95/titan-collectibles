from flask import Blueprint, jsonify
from models import db, CardInstance, CardTemplate, Athlete
from flask_login import current_user

bp = Blueprint('cards_api', __name__, url_prefix='/api/cards')

@bp.get('/<uuid:card_id>')
def get_card(card_id):
    inst = db.session.get(CardInstance, card_id)
    if not inst: return jsonify({'error':'not found'}), 404
    tpl = db.session.get(CardTemplate, inst.template_id)
    ath = db.session.get(Athlete, tpl.athlete_id)
    owned_by_me = bool(inst.owner_user_id) and current_user.is_authenticated and str(inst.owner_user_id)==str(current_user.id)
    return jsonify({
        'id': str(inst.id), 'owned': bool(inst.owner_user_id), 'ownedByMe': owned_by_me, 'serial_no': inst.serial_no,
        'template': {
            'version': tpl.version,
            'glb_url': tpl.glb_url,
            'athlete': {
                'full_name': ath.full_name,
                'dob': ath.dob.isoformat() if ath.dob else None,
                'sport': ath.sport,
                'nationality': ath.nationality,
                'handedness': ath.handedness,
                'world_ranking': ath.world_ranking,
                'best_world_ranking': ath.best_world_ranking,
                'intl_debut_year': ath.intl_debut_year,
            }
        }
    })

@bp.post('/<uuid:card_id>/claim')
def claim(card_id):
    inst = db.session.get(CardInstance, card_id)
    if not inst: return jsonify({'error':'not found'}), 404
    if inst.owner_user_id: return jsonify({'error':'already owned'}), 409
    # TODO: replace with real auth; demo user id placeholder
    import uuid
    inst.owner_user_id = uuid.UUID('00000000-0000-0000-0000-000000000001')
    db.session.commit()
    return jsonify({'ok': True})
