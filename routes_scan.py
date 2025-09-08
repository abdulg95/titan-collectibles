from flask import Blueprint, request, jsonify
from sqlalchemy import select
from models import db, CardTemplate, CardInstance, ScanEvent
import os, requests

bp = Blueprint('scan_api', __name__, url_prefix='/api/scan')
ETRNL_URL = 'https://third-party.etrnl.app/v1/tags/verify-authenticity'
ETRNL_KEY = os.environ['ETRNL_PRIVATE_KEY']


def _g(param, *alts):
    """Get a query arg by primary name or any alternates."""
    v = request.args.get(param)
    if v:
        return v
    for a in alts:
        v = request.args.get(a)
        if v:
            return v
    return None


def _resolve_core(template_hint: str | None, tag_id_hint: str | None):
    # Accept both long & short param keys, and path-provided IDs.
    tag_id = tag_id_hint or _g('tagId', 'tid')
    enc    = _g('enc', 'e')
    eCode  = _g('eCode', 'de')
    tt     = _g('tt')                 # tamper token (tamper mode)
    cmac   = _g('cmac', 'c')          # MAC (non-tamper mode)
    templ  = template_hint or _g('t', 'template', 'templateId')

    # Basic validation
    if not tag_id or not enc or not eCode or not (tt or cmac):
        return jsonify({
            'ok': False,
            'reason': 'missing_params',
            'need': 'tagId enc eCode and tt (tamper) OR cmac (mac)'
        }), 400

    # Call ETRNL
    payload = {'tagId': tag_id, 'eCode': eCode, 'enc': enc}
    if tt:
        payload['tt'] = tt
    else:
        payload['cmac'] = cmac

    r = requests.post(
        ETRNL_URL,
        json=payload,
        headers={'API-KEY': ETRNL_KEY, 'Content-Type': 'application/json'},
        timeout=10
    )
    data = r.json()
    if not data.get('success') or not data.get('authentic'):
        return jsonify({'ok': False, 'reason': 'not_authentic'}), 400

    uid = data.get('uid')
    ctr = int(data.get('ctr', 0) or 0)

    # Known tag? (already minted/claimed path)
    inst = db.session.execute(
        select(CardInstance).where(CardInstance.etrnl_tag_uid == uid)
    ).scalar_one_or_none()

    if inst:
        # Replay protection
        if ctr <= (inst.last_ctr or 0):
            return jsonify({'ok': False, 'reason': 'replay'}), 409

        inst.last_ctr = ctr
        db.session.add(ScanEvent(
            card_instance_id=inst.id,
            tag_id=tag_id,
            uid=uid,
            ctr=ctr,
            authentic=True,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            tt_curr=data.get('ttCurrStatus'),
            tt_perm=data.get('ttPermStatus'),
        ))
        db.session.commit()

        state = 'unclaimed' if not inst.owner_user_id else 'owned_by_other'
        return jsonify({'ok': True, 'state': state, 'cardId': str(inst.id)})

    # First time seeing this tag -> need template hint (from path or legacy ?t=)
    if not templ:
        return jsonify({'ok': False, 'reason': 'missing_template_hint'}), 400

    template = db.session.get(CardTemplate, templ)
    if not template:
        return jsonify({'ok': False, 'reason': 'unknown_template'}), 404

    # Mint new CardInstance atomically and log scan
    with db.session.begin():
        template = db.session.execute(
            select(CardTemplate).where(CardTemplate.id == templ).with_for_update()
        ).scalar_one()
        template.minted_count = (template.minted_count or 0) + 1

        inst = CardInstance(
            template_id=template.id,
            serial_no=template.minted_count,
            etrnl_tag_uid=uid,
            etrnl_tag_id=tag_id,
            last_ctr=ctr,
        )
        db.session.add(inst)
        db.session.add(ScanEvent(
            card_instance_id=inst.id,
            tag_id=tag_id,
            uid=uid,
            ctr=ctr,
            authentic=True,
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            tt_curr=data.get('ttCurrStatus'),
            tt_perm=data.get('ttPermStatus'),
        ))

    return jsonify({'ok': True, 'state': 'unclaimed', 'cardId': str(inst.id)})


# --- Legacy shape: /api/scan/resolve?tagId=...&enc=...&tt=...&eCode=...&t=<template_id>
@bp.get('/resolve')
def resolve():
    return _resolve_core(template_hint=None, tag_id_hint=None)


# --- New shape: /api/scan/<template_id>/<tag_id>?enc=...&tt=...&eCode=...
@bp.get('/<templ>/<tag_id>')
def resolve_path(templ, tag_id):
    return _resolve_core(template_hint=templ, tag_id_hint=tag_id)
