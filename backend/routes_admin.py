
from flask import Blueprint, request, jsonify
from sqlalchemy import select
from models import db, CardTemplate, CardInstance
import os, requests


from functools import wraps
import os
from flask import request, abort

ADMIN_TOKEN = os.environ.get('ADMIN_SHARED_TOKEN','')

def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Check header or cookie
        provided = request.headers.get('X-Admin-Token') or request.cookies.get('admin_token')
        if not ADMIN_TOKEN or provided != ADMIN_TOKEN:
            abort(401)
        return fn(*args, **kwargs)
    return wrapper
bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')

ETRNL_URL = 'https://third-party.etrnl.app/v1/tags/verify-authenticity'
ETRNL_KEY = os.environ.get('ETRNL_PRIVATE_KEY')

def verify_with_etrnl(payload):
    r = requests.post(ETRNL_URL, json=payload, headers={'API-KEY': ETRNL_KEY, 'Content-Type':'application/json'}, timeout=10)
    j = r.json()
    return j

@bp.get('/templates')
@require_admin
def list_templates():
    rows = db.session.execute(select(CardTemplate)).scalars().all()
    out = []
    for t in rows:
        out.append({
            'id': str(t.id),
            'version': t.version,
            'athlete_id': str(t.athlete_id),
            'glb_url': t.glb_url,
            'image_url': t.image_url,
            'minted_count': t.minted_count or 0,
            'edition_cap': t.edition_cap,
            'etrnl_url_group_id': t.etrnl_url_group_id
        })
    return jsonify(out)

@bp.post('/bind')
@require_admin
def bind_by_scan():
    """
    Body can be either:
    { "templateId": "...", "tagId":"...", "enc":"...", "eCode":"...", "cmac":"..." }  # or with "tt"
    or: { "templateId": "...", "uid":"...", "tagId":"..." }  # but this path is less secure; prefer verify
    """
    data = request.get_json(force=True)
    template_id = data.get('templateId')
    if not template_id:
        return jsonify({'error':'templateId required'}), 400

    # Prefer verifying via ETRNL if enc/eCode present
    uid = data.get('uid')
    if 'enc' in data and 'eCode' in data and 'tagId' in data:
        payload = {'tagId': data['tagId'], 'eCode': data['eCode'], 'enc': data['enc']}
        if 'tt' in data: payload['tt'] = data['tt']
        elif 'cmac' in data: payload['cmac'] = data['cmac']
        res = verify_with_etrnl(payload)
        if not res.get('success') or not res.get('authentic'):
            return jsonify({'error':'tag not authentic'}), 400
        uid = res.get('uid')
        ctr = int(res.get('ctr', 0))
    elif uid and data.get('tagId'):
        ctr = 0
    else:
        return jsonify({'error':'provide (enc,eCode,tagId,cmac/tt) or (uid,tagId)'}), 400

    # Check not already bound
    existing = db.session.execute(select(CardInstance).where(CardInstance.etrnl_tag_uid==uid)).scalar_one_or_none()
    if existing:
        return jsonify({'error':'already bound', 'cardId': str(existing.id)}), 409

    # Mint instance
    from sqlalchemy import select as sel
    template = db.session.get(CardTemplate, template_id)
    if not template:
        return jsonify({'error':'unknown template'}), 404

    with db.session.begin_nested():  # works even if a transaction is already active
        t_locked = db.session.execute(
            select(CardTemplate)
            .where(CardTemplate.id == (templ or template.id))
            .with_for_update()
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
        db.session.flush()  # ensure inst.id is available for the ScanEvent

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
    return jsonify({'ok': True, 'state': 'unclaimed', 'cardId': str(inst.id)})
