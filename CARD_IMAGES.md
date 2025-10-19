# Adding Card Images

## Quick Setup

### 1. Prepare Your Card Images

You need **18 card images** (one for each template). Name them according to the SKU from `backend/templates.csv`:

```
BE-REG.png  - Brady Ellison Regular
BE-DIA.png  - Brady Ellison Diamond
MG-REG.png  - Mete Gazoz Regular
MG-DIA.png  - Mete Gazoz Diamond
EG-REG.png  - Ella Gibson Regular
EG-DIA.png  - Ella Gibson Diamond
DK-REG.png  - Deepika Kumari Regular
DK-DIA.png  - Deepika Kumari Diamond
SL-REG.png  - Sara Lopez Regular
SL-DIA.png  - Sara Lopez Diamond
MS-REG.png  - Mike Schloesser Regular
MS-DIA.png  - Mike Schloesser Diamond
LS-REG.png  - Lim Sihyeon Regular
LS-DIA.png  - Lim Sihyeon Diamond
MF-REG.png  - Matias Fullerton Regular
MF-DIA.png  - Matias Fullerton Diamond
KW-REG.png  - Kim Woojin Regular
KW-DIA.png  - Kim Woojin Diamond
```

**Image Format Recommendations:**
- Format: PNG (with transparency if needed) or JPG
- Dimensions: 345px width × 483px height (or larger, maintaining aspect ratio ~3:4.2)
- File size: < 500KB each for fast loading

### 2. Place Images in the Assets Folder

Copy all your card images to:
```
frontend/public/assets/cards/
```

The directory has already been created for you.

### 3. Update the Database

Run this command to link the images to your templates:

```bash
cd backend
DATABASE_URL=postgresql://localhost/dscards ./venv/bin/python -m scripts.update_template_images
```

This will update all templates with `image_url = "/assets/cards/{SKU}.png"`

### 4. Restart Your Backend

If your backend is running, restart it:

```bash
cd backend
source venv/bin/activate
DATABASE_URL=postgresql://localhost/dscards python app.py
```

### 5. Test It!

1. Go to `http://localhost:5173/dev/scan`
2. Click "📱 Scan Tag" on any template
3. You'll now see your custom card image on the card view page!

## What Gets Displayed

The card view page will show:
- ✅ Your uploaded card image (top of page)
- ✅ About section (DOB, age, rankings, nationality, etc.)
- ✅ Bio section
- ✅ Top achievements with medals
- ✅ Socials (Instagram, Facebook)
- ✅ Sponsors
- ✅ Floating + button (to add to collection)

## Image Sources

If you don't have card images yet, you can:
- Use AI generators (Midjourney, DALL-E, etc.)
- Commission a designer
- Use placeholder images temporarily
- Create them in Photoshop/Figma

## Fallback

If a template doesn't have an `image_url` set, the system will try to use the athlete's `card_image_url` as a fallback.

