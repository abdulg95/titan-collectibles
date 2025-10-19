from flask import Blueprint, jsonify, session
from models import db, CardInstance, CardTemplate, Athlete, CardStatus
import uuid as uuidlib

bp = Blueprint('cards_api', __name__, url_prefix='/api/cards')

def _uuid(val):
    try: return uuidlib.UUID(str(val))
    except Exception: return None

@bp.get('/<uuid:card_id>')
def get_card(card_id):
    inst = db.session.get(CardInstance, card_id)
    if not inst: return jsonify({'error':'not found'}), 404
    tpl = db.session.get(CardTemplate, inst.template_id)
    ath = db.session.get(Athlete, tpl.athlete_id)
    
    uid = _uuid(session.get('uid'))
    owned_by_me = bool(inst.owner_user_id) and uid and str(inst.owner_user_id) == str(uid)
    
    # Construct card image URL based on version (regular or diamond)
    card_image_url = ath.card_image_url
    if card_image_url and not card_image_url.endswith('.png'):
        # If card_image_url is a base path like "/assets/cards/BE"
        # append -REG.png or -DIA.png based on template version
        suffix = '-DIA.png' if tpl.version == 'diamond' else '-REG.png'
        card_image_url = card_image_url + suffix
    
    return jsonify({
        'id': str(inst.id), 
        'owned': bool(inst.owner_user_id), 
        'ownedByMe': owned_by_me, 
        'serial_no': inst.serial_no,
        'status': inst.status.value if hasattr(inst.status, 'value') else str(inst.status),
        'template': {
            'version': tpl.version,
            'glb_url': tpl.glb_url,
            'image_url': tpl.image_url,
                'athlete': {
                'full_name': ath.full_name,
                'series_number': ath.series_number,
                'card_number': ath.card_number,
                'dob': ath.dob.isoformat() if ath.dob else None,
                'sport': ath.sport,
                'discipline': ath.discipline.value if hasattr(ath.discipline, 'value') else ath.discipline,
                'nationality': ath.nationality,
                'hometown': ath.hometown,
                'handedness': ath.handedness.value if hasattr(ath.handedness, 'value') else ath.handedness,
                'world_ranking': ath.world_ranking,
                'best_world_ranking': ath.best_world_ranking,
                'intl_debut_year': ath.intl_debut_year,
                'bio_short': ath.bio_short,
                'bio_long': ath.bio_long,
                'quote_text': ath.quote_text,
                'quote_source': ath.quote_source,
                'card_image_url': card_image_url,
                'card_back_url': ath.card_back_url,
                'hero_image_url': ath.hero_image_url,
                'video_url': ath.video_url,
                'quote_photo_url': ath.quote_photo_url,
                'action_photo_url': ath.action_photo_url,
                'qualification_image_url': ath.qualification_image_url,
                'achievements': [
                    {
                        'title': ach.title,
                        'result': ach.result,
                        'medal': ach.medal.value if hasattr(ach.medal, 'value') else ach.medal,
                        'display_order': ach.display_order,
                        'notes': ach.notes
                    }
                    for ach in ath.achievements
                ],
                'equipment': [
                    {
                        'category': eq.category,
                        'brand': eq.brand,
                        'model': eq.model,
                        'display_order': eq.display_order
                    }
                    for eq in ath.equipment
                ],
                'qualifications': [
                    {
                        'year': qual.year,
                        'score': float(qual.score) if qual.score else None,
                        'event': qual.event
                    }
                    for qual in ath.qualifications
                ],
                'stats': {
                    'win_percentage': float(ath.stats.win_percentage) if ath.stats and ath.stats.win_percentage else None,
                    'average_arrow': float(ath.stats.average_arrow) if ath.stats and ath.stats.average_arrow else None,
                    'tiebreak_win_rate': float(ath.stats.tiebreak_win_rate) if ath.stats and ath.stats.tiebreak_win_rate else None,
                    'extras': ath.stats.extras if ath.stats and ath.stats.extras else {}
                },
                'socials': ath.socials or {},
                'sponsors': ath.sponsors or []
            }
        }
    })

@bp.post('/<uuid:card_id>/claim')
def claim(card_id):
    uid = _uuid(session.get('uid'))
    if not uid:
        return jsonify({'error': 'unauthorized', 'message': 'You must be logged in to claim a card'}), 401
    
    inst = db.session.get(CardInstance, card_id)
    if not inst: 
        return jsonify({'error':'not found'}), 404
    
    if inst.owner_user_id: 
        return jsonify({'error':'already claimed', 'message': 'This card has already been claimed'}), 409
    
    # Assign to the authenticated user and mark as claimed
    inst.owner_user_id = uid
    inst.status = CardStatus.claimed
    db.session.commit()
    
    return jsonify({'ok': True, 'message': 'Card successfully added to your collection'})
