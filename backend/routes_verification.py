# routes_verification.py

from flask import Blueprint, request, jsonify
from sqlalchemy import select, or_
from models import db, CardTemplate, CardInstance, ScanEvent
import os, requests, uuid

bp = Blueprint('verification_api', __name__, url_prefix='/api/verification')

# New in-house verification service configuration
TITAN_NFC_URL = os.environ.get('TITAN_NFC_URL')
TITAN_NFC_KEY = os.environ.get('TITAN_NFC_KEY')

def _g(param, *alts):
    """Get parameter from request args with alternatives."""
    v = request.args.get(param)
    if v: return v
    for a in alts:
        v = request.args.get(a)
        if v: return v
    return None

def _find_template(hint: str | None) -> CardTemplate | None:
    """Resolve a template by UUID id, template_code, or ETRNL/CSV id."""
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
    # Try template_code (new format) and legacy external ids
    return db.session.execute(
        select(CardTemplate).where(
            or_(
                CardTemplate.template_code == hint,           # new: e.g. 000000000002
                CardTemplate.etrnl_url_group_id == hint       # legacy: e.g. 000000000009
            )
        )
    ).scalar_one_or_none()

def _verify_with_titan_nfc(tag_id: str, encrypted_data: str) -> dict:
    """Verify card authenticity with the new Titan NFC service."""
    try:
        response = requests.get(
            TITAN_NFC_URL,
            params={
                'id': tag_id,
                'data': encrypted_data
            },
            headers={
                'Authorization': TITAN_NFC_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict):
                    return {
                        'success': True,
                        'authentic': data.get('authentic', False),
                        'data': data
                    }
                else:
                    # Handle case where response is not a dict (e.g., boolean)
                    return {
                        'success': True,
                        'authentic': bool(data),
                        'data': data
                    }
            except ValueError:
                # Handle case where response is not valid JSON
                return {
                    'success': True,
                    'authentic': False,
                    'data': response.text
                }
        else:
            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'authentic': False
            }
            
    except requests.RequestException as e:
        return {
            'success': False,
            'error': str(e),
            'authentic': False
        }

def _resolve_core(template_hint: str | None, tag_id_hint: str | None):
    """Core verification logic for the new system."""
    tag_id = tag_id_hint or _g('tagId', 'tid', 'id')
    encrypted_data = _g('data', 'enc', 'encrypted')
    template_hint = template_hint or _g('t', 'template', 'templateId')

    # Validate required parameters
    if not tag_id or not encrypted_data:
        return jsonify({
            'ok': False, 
            'reason': 'missing_params',
            'need': 'tagId (id) and data (encrypted) parameters'
        }), 400

    # Verify with new Titan NFC service
    verification_result = _verify_with_titan_nfc(tag_id, encrypted_data)
    
    if not verification_result['success']:
        return jsonify({
            'ok': False, 
            'reason': 'verification_service_error',
            'error': verification_result.get('error')
        }), 502

    if not verification_result['authentic']:
        return jsonify({
            'ok': False, 
            'reason': 'not_authentic'
        }), 400

    # Check if we already have a card instance for this tag_id
    existing_instance = db.session.execute(
        select(CardInstance).where(CardInstance.etrnl_tag_id == tag_id)
    ).scalar_one_or_none()

    if existing_instance:
        # Re-scan of existing card
        # Update scan event
        db.session.add(ScanEvent(
            card_instance_id=existing_instance.id,
            tag_id=tag_id,
            uid=tag_id,  # Using tag_id as UID for new system
            ctr=1,  # Simple counter for new system
            authentic=True,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            tt_curr=verification_result['data'].get('status'),
            tt_perm=verification_result['data'].get('permanent_status'),
        ))
        db.session.commit()

        state = 'unclaimed' if not existing_instance.owner_user_id else 'owned_by_other'
        return jsonify({
            'ok': True, 
            'state': state, 
            'cardId': str(existing_instance.id), 
            'minted': False,
            'verification_service': 'titan_nfc'
        })

    # First scan - mint new card instance
    template = _find_template(template_hint)
    if not template:
        return jsonify({
            'ok': False, 
            'reason': 'unknown_template',
            'hint': template_hint
        }), 404

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
                etrnl_tag_uid=tag_id,  # Using tag_id as UID
                etrnl_tag_id=tag_id,
                last_ctr=1,  # Simple counter for new system
            )
            db.session.add(inst)
            db.session.flush()  # ensure inst.id exists

            db.session.add(ScanEvent(
                card_instance_id=inst.id,
                tag_id=tag_id,
                uid=tag_id,
                ctr=1,
                authentic=True,
                ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                tt_curr=verification_result['data'].get('status'),
                tt_perm=verification_result['data'].get('permanent_status'),
            ))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'ok': False, 
            'reason': 'mint_failed', 
            'error': str(e)
        }), 500

    return jsonify({
        'ok': True, 
        'state': 'unclaimed', 
        'cardId': str(inst.id), 
        'minted': True,
        'verification_service': 'titan_nfc',
        'serial_no': next_serial
    })

@bp.get('/verify')
def verify_card():
    """Verify a card using the new Titan NFC service."""
    return _resolve_core(template_hint=None, tag_id_hint=None)

@bp.get('/verify/<template_code>/<tag_id>')
def verify_card_with_template(template_code, tag_id):
    """Verify a card with template code and tag ID."""
    return _resolve_core(template_hint=template_code, tag_id_hint=tag_id)

@bp.get('/scan/<template_code>/<tag_id>')
def scan_card_with_template(template_code, tag_id):
    """Legacy endpoint for backward compatibility."""
    return _resolve_core(template_hint=template_code, tag_id_hint=tag_id)

@bp.get('/dev/templates')
def dev_list_templates():
    """DEV ONLY: List all templates for the dev scan UI."""
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
            'verification_url': f'https://titansportshq.com/scan?t={t.template_code}' if t.template_code else None
        })
    
    return jsonify({'templates': templates})

@bp.post('/dev/fake-verify')
def dev_fake_verify():
    """
    DEV ONLY: Simulate a Titan NFC verification without calling the external API.
    Generates fake verification data and mints a card instance.
    
    Body: { "template_code": "000000000002", "tag_id": "fake-tag-123" }
    """
    import secrets
    
    # Only allow in development
    if os.getenv('FLASK_ENV') == 'production':
        return jsonify({'ok': False, 'reason': 'dev_only'}), 403
    
    data = request.get_json() or {}
    template_code = data.get('template_code')
    tag_id = data.get('tag_id', f'fake-{secrets.token_hex(6)}')
    
    if not template_code:
        return jsonify({'ok': False, 'reason': 'missing_template_code'}), 400
    
    # Find the template
    template = _find_template(template_code)
    if not template:
        return jsonify({'ok': False, 'reason': 'template_not_found'}), 404
    
    # Check if this is a re-scan
    existing = db.session.execute(
        select(CardInstance).where(CardInstance.etrnl_tag_id == tag_id)
    ).scalar_one_or_none()
    
    if existing:
        # Re-scan existing card
        db.session.add(ScanEvent(
            card_instance_id=existing.id,
            tag_id=tag_id,
            uid=tag_id,
            ctr=1,
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
            'verification_service': 'titan_nfc'
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
                etrnl_tag_uid=tag_id,
                etrnl_tag_id=tag_id,
                last_ctr=1,
            )
            db.session.add(inst)
            db.session.flush()
            
            db.session.add(ScanEvent(
                card_instance_id=inst.id,
                tag_id=tag_id,
                uid=tag_id,
                ctr=1,
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
            'verification_service': 'titan_nfc',
            'serial_no': next_serial,
            'tag_id': tag_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'reason': 'mint_failed', 'error': str(e)}), 500
