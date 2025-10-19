# routes_scan.py

from flask import Blueprint, request, jsonify
from sqlalchemy import select, or_
from models import db, CardTemplate, CardInstance, ScanEvent
import os, requests, uuid

bp = Blueprint('scan_api', __name__, url_prefix='/api/scan')
ETRNL_URL = 'https://third-party.etrnl.app/v1/tags/verify-authenticity'
ETRNL_KEY = os.environ.get('ETRNL_PRIVATE_KEY', '')

# Titan NFC verification
TITAN_NFC_URL = os.environ.get('TITAN_NFC_URL', 'https://titan-nfc-144404400823.us-east4.run.app/tags/authenticity')
TITAN_NFC_KEY = os.environ.get('TITAN_NFC_KEY', 'UIZ3GBlAXrfaHtnAoP4fPPeCjs2mYWAw')

def _g(param, *alts):
    v = request.args.get(param)
    if v: return v
    for a in alts:
        v = request.args.get(a)
        if v: return v
    return None

def _find_template(hint: str | None) -> CardTemplate | None:
    """Resolve a template by UUID id, ETRNL/CSV id, or SKU (template_code)."""
    if not hint:
        return None
    # Try UUID (primary key)
    try:
        tid = uuid.UUID(str(hint))
    except Exception:
        tid = None
    if tid:
        t = db.session.get(CardTemplate, tid)
        if t:
            return t
    # Try external ids (your CSV id) and SKU
    return db.session.execute(
        select(CardTemplate).where(
            or_(
                CardTemplate.etrnl_url_group_id == hint,  # e.g. 000000000009
                CardTemplate.template_code == hint        # e.g. SL-REG
            )
        )
    ).scalar_one_or_none()

def _resolve_core(template_hint: str | None, tag_id_hint: str | None):
    tag_id = tag_id_hint or _g('tagId', 'tid')
    enc    = _g('enc', 'e')
    eCode  = _g('eCode', 'de')
    tt     = _g('tt')                 # tamper token (tamper mode)
    cmac   = _g('cmac', 'c')          # MAC (non-tamper mode)
    templ_hint  = template_hint or _g('t', 'template', 'templateId')

    if not tag_id or not enc or not eCode or not (tt or cmac):
        return jsonify({'ok': False, 'reason': 'missing_params',
                        'need': 'tagId enc eCode and tt (tamper) OR cmac (mac)'}), 400

    # Verify with ETRNL
    payload = {'tagId': tag_id, 'eCode': eCode, 'enc': enc}
    if tt: payload['tt'] = tt
    else:  payload['cmac'] = cmac

    try:
        r = requests.post(
            ETRNL_URL, json=payload,
            headers={'API-KEY': ETRNL_KEY, 'Content-Type': 'application/json'},
            timeout=10
        )
        data = r.json()
    except requests.RequestException:
        return jsonify({'ok': False, 'reason': 'verify_upstream_error'}), 502

    if not data.get('success') or not data.get('authentic'):
        return jsonify({'ok': False, 'reason': 'not_authentic'}), 400

    uid = data.get('uid')
    ctr = int(data.get('ctr', 0) or 0)

    # Existing card for this UID?
    inst = db.session.execute(
        select(CardInstance).where(CardInstance.etrnl_tag_uid == uid)
    ).scalar_one_or_none()

    if inst:
        # replay protection
        if ctr <= (inst.last_ctr or 0):
            return jsonify({'ok': False, 'reason': 'replay'}), 409

        inst.last_ctr = ctr
        db.session.add(ScanEvent(
            card_instance_id=inst.id,
            tag_id=tag_id, uid=uid, ctr=ctr,
            authentic=True,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            tt_curr=data.get('ttCurrStatus'),
            tt_perm=data.get('ttPermStatus'),
        ))
        db.session.commit()

        state = 'unclaimed' if not inst.owner_user_id else 'owned_by_other'
        # 🔹 minted=False for subsequent scans
        return jsonify({'ok': True, 'state': state, 'cardId': str(inst.id), 'minted': False})

    # First sighting → resolve template
    template = _find_template(templ_hint)
    if not template:
        return jsonify({'ok': False, 'reason': 'unknown_template'}), 404

    # Mint + log scan (use SAVEPOINT to avoid nested TX errors)
    try:
        with db.session.begin_nested():
            t_locked = db.session.execute(
                select(CardTemplate).where(CardTemplate.id == template.id).with_for_update()
            ).scalar_one()

            next_serial = (t_locked.minted_count or 0) + 1
            t_locked.minted_count = next_serial

            inst = CardInstance(
                template_id=t_locked.id,
                serial_no=next_serial,
                etrnl_tag_uid=uid,
                etrnl_tag_id=tag_id,
                last_ctr=ctr,
            )
            db.session.add(inst)
            db.session.flush()  # ensure inst.id exists

            db.session.add(ScanEvent(
                card_instance_id=inst.id,
                tag_id=tag_id, uid=uid, ctr=ctr,
                authentic=True,
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                tt_curr=data.get('ttCurrStatus'),
                tt_perm=data.get('ttPermStatus'),
            ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # 🔹 minted=True for first-ever scan (warehouse registration)
    return jsonify({'ok': True, 'state': 'unclaimed', 'cardId': str(inst.id), 'minted': True})

@bp.get('/resolve')
def resolve():
    return _resolve_core(template_hint=None, tag_id_hint=None)

@bp.get('/<templ>/<tag_id>')
def resolve_path(templ, tag_id):
    return _resolve_core(template_hint=templ, tag_id_hint=tag_id)

@bp.get('/dev/templates')
def dev_list_templates():
    """
    DEV ONLY: List all templates for the dev scan UI.
    """
    # Only allow in development
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({'ok': False, 'reason': 'dev_only'}), 403
    
    from models import Athlete
    
    rows = db.session.execute(select(CardTemplate)).scalars().all()
    templates = []
    for t in rows:
        athlete = db.session.get(Athlete, t.athlete_id)
        templates.append({
            'id': str(t.id),
            'athlete_name': athlete.full_name if athlete else 'Unknown',
            'version': t.version,
            'template_code': t.template_code,
            'minted_count': t.minted_count or 0,
            'edition_cap': t.edition_cap,
        })
    
    return jsonify({'templates': templates})

@bp.post('/dev/fake-scan')
def dev_fake_scan():
    """
    DEV ONLY: Simulate an ETRNL tag scan without calling the external API.
    Generates random tag credentials and mints a card instance.
    
    Body: { "template_id": "uuid" } or { "template_code": "code" }
    """
    import secrets
    
    # Only allow in development
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({'ok': False, 'reason': 'dev_only'}), 403
    
    data = request.get_json() or {}
    template_hint = data.get('template_id') or data.get('template_code')
    
    if not template_hint:
        return jsonify({'ok': False, 'reason': 'missing_template'}), 400
    
    # Find the template
    template = _find_template(template_hint)
    if not template:
        return jsonify({'ok': False, 'reason': 'template_not_found'}), 404
    
    # Generate fake ETRNL tag data
    fake_uid = secrets.token_hex(8)  # 16 char hex string
    fake_tag_id = f"fake-{secrets.token_hex(6)}"
    fake_ctr = 1
    
    # Check if this is a re-scan (for testing re-scan flow)
    force_new = data.get('force_new', True)
    
    if not force_new:
        # Check if we already have a card with this fake UID (for re-scan testing)
        existing = db.session.execute(
            select(CardInstance).where(CardInstance.etrnl_tag_uid == fake_uid)
        ).scalar_one_or_none()
        
        if existing:
            existing.last_ctr = fake_ctr
            db.session.add(ScanEvent(
                card_instance_id=existing.id,
                tag_id=fake_tag_id,
                uid=fake_uid,
                ctr=fake_ctr,
                authentic=True,
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
            ))
            db.session.commit()
            
            state = 'unclaimed' if not existing.owner_user_id else 'owned_by_other'
            return jsonify({
                'ok': True, 
                'state': state, 
                'cardId': str(existing.id), 
                'minted': False,
                'dev_mode': True,
                'fake_uid': fake_uid,
                'fake_tag_id': fake_tag_id
            })
    
    # Mint new card instance
    try:
        with db.session.begin_nested():
            t_locked = db.session.execute(
                select(CardTemplate).where(CardTemplate.id == template.id).with_for_update()
            ).scalar_one()
            
            next_serial = (t_locked.minted_count or 0) + 1
            t_locked.minted_count = next_serial
            
            inst = CardInstance(
                template_id=t_locked.id,
                serial_no=next_serial,
                etrnl_tag_uid=fake_uid,
                etrnl_tag_id=fake_tag_id,
                last_ctr=fake_ctr,
            )
            db.session.add(inst)
            db.session.flush()
            
            db.session.add(ScanEvent(
                card_instance_id=inst.id,
                tag_id=fake_tag_id,
                uid=fake_uid,
                ctr=fake_ctr,
                authentic=True,
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
            ))
        
        db.session.commit()
        
        return jsonify({
            'ok': True,
            'state': 'unclaimed',
            'cardId': str(inst.id),
            'minted': True,
            'dev_mode': True,
            'fake_uid': fake_uid,
            'fake_tag_id': fake_tag_id,
            'serial_no': next_serial
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'reason': 'mint_failed', 'error': str(e)}), 500

# Titan NFC verification endpoint
@bp.route('/verify', methods=['GET'])
def verify_titan_nfc():
    """Verify a card using Titan NFC service"""
    try:
        card_id = request.args.get('id')
        data = request.args.get('data')
        
        if not card_id or not data:
            return jsonify({'ok': False, 'reason': 'missing_params'}), 400
        
        # Call Titan NFC verification service
        headers = {
            'Authorization': f'Bearer {TITAN_NFC_KEY}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'id': card_id,
            'data': data
        }
        
        response = requests.get(TITAN_NFC_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('authentic', False):
                # Find the card template
                template = _find_template(card_id)
                if template:
                    return jsonify({
                        'ok': True,
                        'authentic': True,
                        'template': {
                            'id': str(template.id),
                            'template_code': template.template_code,
                            'version': template.version,
                            'athlete_id': template.athlete_id
                        }
                    })
                else:
                    return jsonify({'ok': False, 'reason': 'template_not_found'}), 404
            else:
                return jsonify({'ok': False, 'reason': 'not_authentic'}), 400
        else:
            return jsonify({'ok': False, 'reason': 'verification_failed'}), 500
            
    except Exception as e:
        return jsonify({'ok': False, 'reason': 'error', 'error': str(e)}), 500