from flask import Blueprint, request, jsonify
from sqlalchemy import select
from models import db, CardTemplate, CardInstance, ScanEvent
import os, requests

bp = Blueprint('scan_api', __name__, url_prefix='/api/scan')
ETRNL_URL = 'https://third-party.etrnl.app/v1/tags/verify-authenticity'
ETRNL_KEY = os.environ['ETRNL_PRIVATE_KEY']

@bp.get('/resolve')
def resolve():
    tag_id = request.args.get('tagId'); enc = request.args.get('enc'); eCode = request.args.get('eCode')
    cmac = request.args.get('cmac'); tt = request.args.get('tt'); templ = request.args.get('t')  # template_id hint

    payload = {'tagId': tag_id, 'eCode': eCode, 'enc': enc}
    if tt: payload['tt'] = tt
    elif cmac: payload['cmac'] = cmac

    r = requests.post(ETRNL_URL, json=payload, headers={'API-KEY': ETRNL_KEY, 'Content-Type':'application/json'}, timeout=10)
    data = r.json()
    if not data.get('success') or not data.get('authentic'):
        return jsonify({'ok': False, 'reason': 'not_authentic'}), 400

    uid = data.get('uid'); ctr = int(data.get('ctr', 0))

    inst = db.session.execute(select(CardInstance).where(CardInstance.etrnl_tag_uid==uid)).scalar_one_or_none()

    if inst:
        if ctr <= (inst.last_ctr or 0):
            return jsonify({'ok': False, 'reason': 'replay'}), 409
        inst.last_ctr = ctr
        db.session.add(ScanEvent(card_instance_id=inst.id, tag_id=tag_id, uid=uid, ctr=ctr,
                                 authentic=True, ip=request.remote_addr, user_agent=request.headers.get('User-Agent'),
                                 tt_curr=data.get('ttCurrStatus'), tt_perm=data.get('ttPermStatus')))
        db.session.commit()
        state = 'unclaimed' if not inst.owner_user_id else 'owned'
        return jsonify({'ok': True, 'state': 'unclaimed' if state=='unclaimed' else 'owned_by_other', 'cardId': str(inst.id)})

    if not templ:
        return jsonify({'ok': False, 'reason': 'missing_template_hint'}), 400
    template = db.session.get(CardTemplate, templ)
    if not template:
        return jsonify({'ok': False, 'reason': 'unknown_template'}), 404

    with db.session.begin():
        template = db.session.execute(select(CardTemplate).where(CardTemplate.id==templ).with_for_update()).scalar_one()
        template.minted_count = (template.minted_count or 0) + 1
        inst = CardInstance(template_id=template.id, serial_no=template.minted_count,
                            etrnl_tag_uid=uid, etrnl_tag_id=tag_id, last_ctr=ctr)
        db.session.add(inst)
        db.session.add(ScanEvent(card_instance_id=inst.id, tag_id=tag_id, uid=uid, ctr=ctr,
                                 authentic=True, ip=request.remote_addr, user_agent=request.headers.get('User-Agent'),
                                 tt_curr=data.get('ttCurrStatus'), tt_perm=data.get('ttPermStatus')))

    return jsonify({'ok': True, 'state': 'unclaimed', 'cardId': str(inst.id)})
