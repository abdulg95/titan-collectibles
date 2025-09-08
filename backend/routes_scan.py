# routes_scan.py  (drop-in)

from flask import Blueprint, request, jsonify
from sqlalchemy import select, or_
from models import db, CardTemplate, CardInstance, ScanEvent
import os, requests, uuid

bp = Blueprint('scan_api', __name__, url_prefix='/api/scan')
ETRNL_URL = 'https://third-party.etrnl.app/v1/tags/verify-authenticity'
ETRNL_KEY = os.environ['ETRNL_PRIVATE_KEY']

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

    payload = {'tagId': tag_id, 'eCode': eCode, 'enc': enc}
    if tt: payload['tt'] = tt
    else:  payload['cmac'] = cmac

    # Call ETRNL (defensive network handling)
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
        return jsonify({'ok': True, 'state': state, 'cardId': str(inst.id)})

    # First sighting → resolve template (accept UUID, CSV id, or SKU)
    template = _find_template(templ_hint)
    if not template:
        return jsonify({'ok': False, 'reason': 'unknown_template'}), 404

    # ---- FIX: use a SAVEPOINT to avoid "transaction already begun" ----
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

    return jsonify({'ok': True, 'state': 'unclaimed', 'cardId': str(inst.id)})

@bp.get('/resolve')
def resolve():
    return _resolve_core(template_hint=None, tag_id_hint=None)

@bp.get('/<templ>/<tag_id>')
def resolve_path(templ, tag_id):
    return _resolve_core(template_hint=templ, tag_id_hint=tag_id)