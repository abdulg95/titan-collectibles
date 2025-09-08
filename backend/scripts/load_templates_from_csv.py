#!/usr/bin/env python3
"""
Load/Upsert CardTemplate rows from templates.csv

CSV header expected:
  template_id,display_name,version,sku

- template_id in CSV is the external ETRNL group id; we store it in CardTemplate.etrnl_url_group_id
- sku becomes CardTemplate.template_code (unique)
- version must be 'regular' or 'diamond'
- Athlete is matched by a slug from the display_name prefix (before '—' or '-').

Usage (local):
  python -m scripts.load_templates_from_csv ./templates.csv
  python -m scripts.load_templates_from_csv ./templates.csv --dry-run

Usage (Heroku):
  heroku run python scripts/load_templates_from_csv.py /app/templates.csv -a <backend-app>
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path
from typing import Optional

from app import app, db
from models import Athlete, CardTemplate

ALLOWED_VERSIONS = {"regular", "diamond"}

# If any CSV display_name needs a manual mapping to an existing slug, add it here.
OVERRIDES = {
    # "Brady Ellison — Regular": "brady-ellison",
    # "Deepika Kumari - Diamond": "deepika-kumari",
}

def _slugify_name(s: str) -> str:
    """
    Take the part before an em dash or hyphen (e.g., 'Brady Ellison — Regular' -> 'Brady Ellison'),
    strip accents, downcase, and convert to a URL-safe slug.
    """
    if not s:
        return ""
    name_only = re.split(r"\s+[—-]\s+", s, maxsplit=1)[0]
    n = unicodedata.normalize("NFKD", name_only).encode("ascii", "ignore").decode("ascii")
    n = n.lower().strip()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    return n

def _display_name_to_slug(display_name: str) -> str:
    key = display_name.strip().lower()
    for k, v in OVERRIDES.items():
        if key == k.strip().lower():
            return v
    return _slugify_name(display_name)

def _get_or_create_athlete(athlete_display_name: str) -> Athlete:
    slug = _display_name_to_slug(athlete_display_name)
    a = Athlete.query.filter_by(slug=slug).first()
    if a:
        return a
    # store clean name (before dash)
    import re
    clean_name = re.split(r"\s+[—-]\s+", athlete_display_name, maxsplit=1)[0].strip()
    a = Athlete(full_name=clean_name, slug=slug, sport="Archery")
    db.session.add(a)
    db.session.flush()
    print(f"Created placeholder Athlete: {a.full_name} (slug={a.slug})")
    return a


def _find_existing_template(athlete_id, version: str, sku: str, ext_group_id: str) -> Optional[CardTemplate]:
    """
    Try to locate an existing CardTemplate by the safest keys first:
      1) template_code (SKU) if present
      2) etrnl_url_group_id (external group id) if present
      3) (athlete_id, version) pair
    """
    if sku:
        t = CardTemplate.query.filter_by(template_code=sku).first()
        if t:
            return t
    if ext_group_id:
        t = CardTemplate.query.filter_by(etrnl_url_group_id=ext_group_id).first()
        if t:
            return t
    return (
        CardTemplate.query
        .filter_by(athlete_id=athlete_id, version=version)
        .first()
    )

def upsert_template(row: dict, dry_run: bool = False):
    display_name = (row.get("display_name") or "").strip()
    version = (row.get("version") or "").strip().lower()
    sku = (row.get("sku") or "").strip()  # will be stored as template_code
    ext_group_id = (row.get("template_id") or "").strip()  # store in etrnl_url_group_id

    if not display_name or not version:
        print(f"Skipping row (missing display_name/version): {row}")
        return
    if version not in ALLOWED_VERSIONS:
        raise SystemExit(f"CSV version '{version}' must be one of {sorted(ALLOWED_VERSIONS)}")

    athlete = _get_or_create_athlete(display_name)

    tmpl = _find_existing_template(athlete.id, version, sku, ext_group_id)
    if tmpl:
        # Update in place
        tmpl.athlete_id = athlete.id
        tmpl.version = version
        if sku:
            tmpl.template_code = sku
        if ext_group_id:
            tmpl.etrnl_url_group_id = ext_group_id
        action = "updated"
    else:
        # Create new
        tmpl = CardTemplate(
            athlete_id=athlete.id,
            version=version,
            template_code=sku or None,
            etrnl_url_group_id=ext_group_id or None,
            minted_count=0,
        )
        db.session.add(tmpl)
        action = "created"

    if dry_run:
        db.session.rollback()
        print(f"[DRY] {action} template for {athlete.full_name} ({version}) sku={sku or '-'} ext_id={ext_group_id or '-'}")
    else:
        db.session.commit()
        print(f"{action} template for {athlete.full_name} ({version}) sku={sku or '-'} ext_id={ext_group_id or '-'}")

def main():
    if len(sys.argv) < 2:
        print("Usage: load_templates_from_csv.py <templates.csv> [--dry-run]")
        sys.exit(2)
    csv_path = Path(sys.argv[1])
    dry = "--dry-run" in sys.argv[2:]

    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    with app.app_context():
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"template_id", "display_name", "version", "sku"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                raise SystemExit(f"CSV must have columns: {sorted(required)}")
            for row in reader:
                upsert_template(row, dry_run=dry)
        if not dry:
            db.session.commit()
    print("Done.")

if __name__ == "__main__":
    main()
