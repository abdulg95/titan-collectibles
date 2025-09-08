#!/usr/bin/env python3
"""
Dev-only helper to spoof/mint card instances without calling ETRNL.

Usage examples (run from backend/ folder, venv active):

  # Mint 1 unclaimed instance by Template UUID
  python scripts/dev_mint.py --template-id 6c7f7d1b-2d05-4b3e-9f8f-886f0b1e61f2

  # Mint and assign 3 instances to a user by email
  python scripts/dev_mint.py --template-id 6c7f7d1b-2d05-4b3e-9f8f-886f0b1e61f2 --email you@example.com --count 3

  # Locate template by athlete slug + version
  python scripts/dev_mint.py --athlete-slug mathias-fullerton --version diamond --email you@example.com

  # Locate template by template_code / SKU (new)
  python scripts/dev_mint.py --template-code KW-DIA --email you@example.com

  # (Legacy) Locate template by stored ETRNL group id
  python scripts/dev_mint.py --group-id abc123 --email you@example.com

On Heroku (replace APP with your backend app name):
  heroku run python scripts/dev_mint.py --template-code KW-DIA --email you@example.com -a <APP>
"""

import argparse
import uuid as _uuid
from datetime import datetime, timezone
import random
import string

from app import app, db
from models import (
    User, Athlete, CardTemplate, CardInstance, ScanEvent,
    CardStatus
)
from sqlalchemy import select
from sqlalchemy.orm import joinedload


def coerce_uuid(s: str):
    try:
        return _uuid.UUID(str(s))
    except Exception:
        return None


def rand_tag(prefix="FAKE"):
    # Short, human-readable fake tag id & uid for testing
    r = ''.join(random.choices(string.digits, k=6))
    uid = ''.join(random.choices('0123456789ABCDEF', k=14))
    return f"{prefix}-{r}", f"UID-{uid}"


def find_template(args) -> CardTemplate | None:
    # 1) By CardTemplate.id (UUID)
    if args.template_id:
        tid = coerce_uuid(args.template_id)
        if not tid:
            raise SystemExit("ERROR: --template-id is not a valid UUID")
        return db.session.get(CardTemplate, tid)

    # 2) By template_code / SKU (new preferred selector)
    if args.template_code:
        return CardTemplate.query.filter(
            CardTemplate.template_code == args.template_code.strip()
        ).first()

    # 3) By legacy ETRNL group id (kept for compatibility)
    if args.group_id:
        return CardTemplate.query.filter_by(etrnl_url_group_id=args.group_id).first()

    # 4) By athlete slug + version
    if args.athlete_slug and args.version:
        return (
            db.session.query(CardTemplate)
            .join(Athlete, Athlete.id == CardTemplate.athlete_id)
            .options(joinedload(CardTemplate.athlete))
            .filter(
                Athlete.slug == args.athlete_slug.strip().lower(),
                CardTemplate.version == args.version.strip().lower(),
            )
            .first()
        )

    return None


def main():
    p = argparse.ArgumentParser(description="Dev mint/spoof card instances")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--template-id", help="CardTemplate.id (UUID)")
    g.add_argument("--template-code", "--sku", dest="template_code", help="CardTemplate.template_code (SKU), e.g. KW-DIA")
    g.add_argument("--group-id", help="(legacy) CardTemplate.etrnl_url_group_id")
    g.add_argument("--athlete-slug", help="find template by athlete slug (use with --version)")

    p.add_argument("--version", help="template version if using --athlete-slug (e.g., regular|diamond)")
    p.add_argument("--email", help="assign minted instances to this user email (optional)")
    p.add_argument("--count", type=int, default=1, help="how many instances to mint (default 1)")
    p.add_argument("--tag-prefix", default="FAKE", help="prefix for generated tagId (default FAKE)")
    args = p.parse_args()

    with app.app_context():
        template = find_template(args)
        if not template:
            raise SystemExit("ERROR: Could not locate CardTemplate with given parameters.")

        user = None
        if args.email:
            user = User.query.filter_by(email=args.email.strip().lower()).first()
            if not user:
                raise SystemExit(f"ERROR: No user found with email {args.email}")

        print("Template:")
        print(f"  id:            {template.id}")
        print(f"  template_code: {getattr(template, 'template_code', None)}")
        print(f"  version:       {template.version}")
        print(f"  athlete_id:    {template.athlete_id}")
        print(f"  minted_count:  {template.minted_count}")
        print(f"  edition_cap:   {template.edition_cap}")
        if user:
            print(f"Assigning to:    {user.email} ({user.id})")
        print(f"Minting count:   {args.count}")

        created = []
        for _ in range(args.count):
            with db.session.begin():
                # Lock template row to avoid race in minted_count
                t_locked = db.session.execute(
                    select(CardTemplate).where(CardTemplate.id == template.id).with_for_update()
                ).scalar_one()

                # Respect edition cap if present
                next_serial = (t_locked.minted_count or 0) + 1
                if t_locked.edition_cap is not None and next_serial > t_locked.edition_cap:
                    raise SystemExit(
                        f"ABORT: edition_cap reached for template {t_locked.id} "
                        f"(cap={t_locked.edition_cap}, current minted={t_locked.minted_count})."
                    )

                t_locked.minted_count = next_serial

                tag_id, uid = rand_tag(prefix=args.tag_prefix)

                inst = CardInstance(
                    template_id=t_locked.id,
                    serial_no=next_serial,
                    etrnl_tag_uid=uid,
                    etrnl_tag_id=tag_id,
                    last_ctr=1,  # pretend first scan already happened
                    owner_user_id=user.id if user else None,
                    status=CardStatus.claimed if user else CardStatus.unassigned,
                )
                db.session.add(inst)

                # Add a "successful scan" event for the audit trail
                db.session.add(ScanEvent(
                    card_instance_id=inst.id,
                    tag_id=tag_id,
                    uid=uid,
                    ctr=1,
                    authentic=True,
                    tt_curr="ok",
                    tt_perm="ok",
                    ip="127.0.0.1",
                    user_agent="dev-spoof/1.0",
                    created_at=datetime.now(timezone.utc)
                ))

                created.append(inst)

        db.session.commit()

        print("\nCreated instances:")
        for inst in created:
            owner = inst.owner_user_id or '-'
            print(
                f"  - CardInstance {inst.id}  serial={inst.serial_no}  "
                f"tagId={inst.etrnl_tag_id}  uid={inst.etrnl_tag_uid}  "
                f"status={inst.status.value}  owner={owner}"
            )


if __name__ == "__main__":
    main()
