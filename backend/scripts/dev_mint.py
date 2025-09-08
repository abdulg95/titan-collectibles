#!/usr/bin/env python3
"""
Dev-only helper to spoof/mint card instances without calling ETRNL.

Examples (run from backend/ with venv active):
  # Mint 1 unclaimed instance
  python -m scripts.dev_mint --athlete-slug brady-ellison --version regular --count 1

  # Mint & assign 3 instances to a user
  python -m scripts.dev_mint --athlete-slug brady-ellison --version regular --email you@example.com --count 3

  # Locate template directly
  python -m scripts.dev_mint --template-id <UUID>
  python -m scripts.dev_mint --group-id 000000000001
"""

import argparse
import os
import random
import string
import uuid as _uuid
from datetime import datetime, timezone

# Ensure app imports even if these aren’t set in dev
os.environ.setdefault("ETRNL_PRIVATE_KEY", "dev-local")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:5173")

from app import app, db
from models import (
    User, Athlete, CardTemplate, CardInstance, ScanEvent, CardStatus
)
from sqlalchemy import select
from sqlalchemy.orm import aliased


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
    # by template-id (UUID PK)
    if args.template_id:
        tid = coerce_uuid(args.template_id)
        if not tid:
            raise SystemExit("ERROR: --template-id is not a valid UUID")
        return db.session.get(CardTemplate, tid)

    # by stored external/group id (string)
    if args.group_id:
        return CardTemplate.query.filter_by(etrnl_url_group_id=args.group_id.strip()).first()

    # by athlete slug + version (no relationship assumptions)
    if args.athlete_slug and args.version:
        A = aliased(Athlete)
        return (
            db.session.query(CardTemplate)
            .join(A, A.id == CardTemplate.athlete_id)
            .filter(
                A.slug == args.athlete_slug.strip().lower(),
                CardTemplate.version == args.version.strip().lower(),
            )
            .first()
        )

    return None


def main():
    p = argparse.ArgumentParser(description="Dev mint/spoof card instances")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--template-id", help="CardTemplate.id (UUID)")
    g.add_argument("--group-id", help="CardTemplate.etrnl_url_group_id")
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

        print("\nTemplate:")
        print(f"  id:            {template.id}")
        print(f"  template_code: {getattr(template, 'template_code', None)}")
        print(f"  version:       {template.version}")
        print(f"  athlete_id:    {template.athlete_id}")
        print(f"  minted_count:  {template.minted_count or 0}")
        print(f"  edition_cap:   {getattr(template, 'edition_cap', None)}")
        print(f"Minting count:   {args.count}")

        # Optional cap check
        cap = getattr(template, "edition_cap", None)
        if cap is not None and (template.minted_count or 0) + args.count > cap:
            raise SystemExit(f"ERROR: edition_cap {cap} would be exceeded.")

        created: list[CardInstance] = []

        # Clear any implicit tx from earlier reads and do one atomic tx
        db.session.rollback()
        with db.session.begin():
            # Lock template row once (prevents race on minted_count)
            t_locked = db.session.execute(
                select(CardTemplate)
                .where(CardTemplate.id == template.id)
                .with_for_update()
            ).scalar_one()

            start_serial = t_locked.minted_count or 0

            for i in range(args.count):
                serial = start_serial + i + 1
                t_locked.minted_count = serial

                tag_id, uid = rand_tag(prefix=args.tag_prefix)

                inst = CardInstance(
                    template_id=t_locked.id,
                    serial_no=serial,
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
                    created_at=datetime.now(timezone.utc),
                ))

                created.append(inst)

        print("\nCreated instances:")
        for inst in created:
            print(
                f"  - CardInstance {inst.id}  serial={inst.serial_no}  "
                f"tagId={inst.etrnl_tag_id}  uid={inst.etrnl_tag_uid}  "
                f"status={inst.status.value}  owner={inst.owner_user_id or '-'}"
            )
        print("Done.\n")


if __name__ == "__main__":
    main()
