# Digital Sports Cards — React + Flask + Shopify + ETRNL Starter

This repo implements a headless storefront in **React/TypeScript** with **Shopify Storefront API** checkout, a **Flask** backend on **Heroku Postgres**, and **ETRNL** NFC verification. It supports the **card template + mint-on-scan card instances** model (unknown physical quantity, 9 athletes × 2 versions).

## Features
- Shopify headless cart → redirect to hosted **checkoutUrl**
- NFC scan → server-side authenticity via ETRNL → mint card instance on first scan
- One-owner claim lock; tamper and replay protection (monotonic `ctr`)
- 3D GLB viewer on card page

## Environment
- Frontend: `VITE_SHOPIFY_STORE_DOMAIN`, `VITE_STOREFRONT_API_TOKEN`, `VITE_API_BASE_URL`
- Backend: `DATABASE_URL`, `FLASK_SECRET_KEY`, `ETRNL_PRIVATE_KEY`, `SHOPIFY_WEBHOOK_SECRET`, `ALLOWED_ORIGINS`

## Setup
### Frontend
```bash
cd frontend
npm i
cp .env.example .env
npm run dev
```

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask db init && flask db migrate -m "init" && flask db upgrade
flask run
```

### Shopify
1. Create **Storefront API token** → set in `frontend/.env`.
2. Create products/variants (1 per **card template**, e.g., 18 total).
3. Add webhook `orders/create` → `/webhooks/shopify/orders_create` and set `SHOPIFY_WEBHOOK_SECRET` in backend.

### ETRNL URL Groups
For each card template create a group with custom URL:
```
https://YOUR_FRONTEND/scan/{tagId}?enc={enc}&eCode={eCode}&cmac={cmac}&t=<TEMPLATE_ID>
```
(Use `tt` instead of `cmac` if tamper is enabled.)

## Deploy (Heroku backend)
```bash
heroku create YOUR-BACKEND-APP
heroku addons:create heroku-postgresql:mini
heroku config:set FLASK_SECRET_KEY=... ETRNL_PRIVATE_KEY=... SHOPIFY_WEBHOOK_SECRET=... ALLOWED_ORIGINS=https://YOUR-FRONTEND
git push heroku main
heroku run flask db upgrade
```

## Notes
- Replace the placeholder auth in `routes_cards.py` with real auth (Flask-Login/JWT).
- Store GLB models on S3/R2; serve via signed URLs.
