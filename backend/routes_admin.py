# routes_admin.py

from functools import wraps
import os
import uuid

from flask import Blueprint, request, jsonify, abort
from sqlalchemy import select, or_

from models import db, CardTemplate, CardInstance, ScanEvent

ADMIN_TOKEN = os.environ.get("ADMIN_SHARED_TOKEN", "")

def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        provided = request.headers.get("X-Admin-Token") or request.cookies.get("admin_token")
        if not ADMIN_TOKEN or provided != ADMIN_TOKEN:
            abort(401)
        return fn(*args, **kwargs)
    return wrapper

bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

ETRNL_URL = "https://third-party.etrnl.app/v1/tags/verify-authenticity"
ETRNL_KEY = os.environ.get("ETRNL_PRIVATE_KEY")

def verify_with_etrnl(payload: dict) -> dict:
    import requests
    r = requests.post(
        ETRNL_URL,
        json=payload,
        headers={"API-KEY": ETRNL_KEY, "Content-Type": "application/json"},
        timeout=10,
    )
    return r.json()

def _resolve_template(hint: str) -> CardTemplate | None:
    """Allow templateId to be DB UUID, CSV/ETRNL id, or SKU (template_code)."""
    if not hint:
        return None
    try:
        tid = uuid.UUID(str(hint))
    except Exception:
        tid = None
    if tid:
        t = db.session.get(CardTemplate, tid)
        if t:
            return t
    return db.session.execute(
        select(CardTemplate).where(
            or_(
                CardTemplate.etrnl_url_group_id == hint,  # e.g. 000000000009
                CardTemplate.template_code == hint,       # e.g. SL-REG
            )
        )
    ).scalar_one_or_none()

@bp.get("/templates")
@require_admin
def list_templates():
    rows = db.session.execute(select(CardTemplate)).scalars().all()
    out = []
    for t in rows:
        out.append({
            "id": str(t.id),
            "version": t.version,
            "athlete_id": str(t.athlete_id),
            "glb_url": t.glb_url,
            "image_url": t.image_url,
            "minted_count": t.minted_count or 0,
            "edition_cap": t.edition_cap,
            "etrnl_url_group_id": t.etrnl_url_group_id,
            "template_code": t.template_code,
        })
    return jsonify(out)

@bp.post("/bind")
@require_admin
def bind_by_scan():
    """
    Bind a scanned tag to a specific template, minting an instance if needed.

    Body options (prefer the verified path):
      { "templateId":"<uuid|sku|ext>", "tagId":"...", "enc":"...", "eCode":"...", "cmac":"..." }
      or with "tt" instead of "cmac".
    Fallback (less secure):
      { "templateId":"<uuid|sku|ext>", "uid":"...", "tagId":"..." }
    """
    data = request.get_json(force=True) or {}
    template_hint = data.get("templateId")
    tag_id = data.get("tagId")

    if not template_hint:
        return jsonify({"error": "templateId required"}), 400

    template = _resolve_template(template_hint)
    if not template:
        return jsonify({"error": "unknown template"}), 404

    uid = data.get("uid")
    ctr = 0
    tt_curr = None
    tt_perm = None

    # Prefer verifying via ETRNL if enc/eCode present
    if tag_id and data.get("enc") and data.get("eCode"):
        payload = {"tagId": tag_id, "eCode": data["eCode"], "enc": data["enc"]}
        if "tt" in data:
            payload["tt"] = data["tt"]
        elif "cmac" in data:
            payload["cmac"] = data["cmac"]

        res = verify_with_etrnl(payload)
        if not res.get("success") or not res.get("authentic"):
            return jsonify({"error": "tag not authentic"}), 400

        uid = res.get("uid")
        ctr = int(res.get("ctr", 0) or 0)
        tt_curr = res.get("ttCurrStatus")
        tt_perm = res.get("ttPermStatus")

    elif uid and tag_id:
        # unverified path (admin-only)
        ctr = 0
    else:
        return jsonify({"error": "provide (enc,eCode,tagId,cmac/tt) or (uid,tagId)"}), 400

    # Already bound?
    existing = db.session.execute(
        select(CardInstance).where(CardInstance.etrnl_tag_uid == uid)
    ).scalar_one_or_none()
    if existing:
        return jsonify({"error": "already bound", "cardId": str(existing.id)}), 409

    # Mint & record
    from sqlalchemy import select as sel
    with db.session.begin_nested():  # safe if a transaction already exists
        t_locked = db.session.execute(
            sel(CardTemplate).where(CardTemplate.id == template.id).with_for_update()
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
        db.session.flush()

        db.session.add(ScanEvent(
            card_instance_id=inst.id,
            tag_id=tag_id,
            uid=uid,
            ctr=ctr,
            authentic=True,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            tt_curr=tt_curr,
            tt_perm=tt_perm,
        ))

    db.session.commit()
    return jsonify({"ok": True, "state": "unclaimed", "cardId": str(inst.id)})