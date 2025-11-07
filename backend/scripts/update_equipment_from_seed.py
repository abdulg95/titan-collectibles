#!/usr/bin/env python3
"""Update only athlete equipment records from the seed file."""

import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402
from models import db, Athlete, AthleteEquipment  # noqa: E402

SEED_PATH = ROOT / "seeds" / "athlete_seed.json"


def load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def update_equipment():
    data = load_seed()
    with app.app_context():
        updated = 0
        missing = []
        for entry in data:
            equipment = entry.get("equipment") or []
            if not equipment:
                continue

            full_name = entry.get("full_name")
            if not full_name:
                continue

            athlete = (
                db.session.query(Athlete)
                .filter(Athlete.full_name == full_name)
                .first()
            )
            if not athlete:
                missing.append(full_name)
                continue

            db.session.query(AthleteEquipment).filter_by(athlete_id=athlete.id).delete()

            for idx, eq in enumerate(equipment):
                item = AthleteEquipment(
                    id=uuid.uuid4(),
                    athlete_id=athlete.id,
                    category=eq.get("category", "Equipment"),
                    brand=eq.get("brand"),
                    model=eq.get("model"),
                    display_order=eq.get("display_order", idx),
                    url=eq.get("url"),
                    notes=eq.get("notes"),
                )
                db.session.add(item)

            updated += 1
            print(f"✅ Updated equipment for {full_name} ({len(equipment)} items)")

        db.session.commit()

        if missing:
            print("⚠️ Could not find athletes in DB:")
            for name in missing:
                print(f"  - {name}")
        print(f"🎯 Equipment update complete for {updated} athletes")


if __name__ == "__main__":
    update_equipment()
