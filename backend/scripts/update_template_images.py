#!/usr/bin/env python3
"""
Update CardTemplate image_url fields with card images.

Usage:
  python -m scripts.update_template_images
  
This script sets image URLs based on the template_code (SKU).
Images should be placed in: frontend/public/assets/cards/{sku}.png
"""
import sys
from pathlib import Path

from app import app, db
from models import CardTemplate

# Base URL for your frontend assets
# In production, this would be your CDN or deployed frontend URL
# For local dev, we'll use relative paths that work with Vite
BASE_URL = "/assets/cards"

def update_template_images():
    """Update all templates with image URLs based on their template_code."""
    
    with app.app_context():
        templates = CardTemplate.query.all()
        
        if not templates:
            print("No templates found in database.")
            return
        
        updated = 0
        for t in templates:
            if not t.template_code:
                print(f"⚠️  Template {t.id} has no template_code, skipping")
                continue
            
            # Build image URL based on template code (e.g., BE-REG → /assets/cards/BE-REG.png)
            image_url = f"{BASE_URL}/{t.template_code}.png"
            
            if t.image_url != image_url:
                t.image_url = image_url
                updated += 1
                print(f"✓ Updated {t.template_code}: {image_url}")
            else:
                print(f"  {t.template_code}: already set")
        
        if updated > 0:
            db.session.commit()
            print(f"\n✅ Updated {updated} template(s)")
        else:
            print("\n✓ All templates already have image URLs")

if __name__ == "__main__":
    update_template_images()

