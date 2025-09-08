# backend/app.py
from flask import Flask
from flask_cors import CORS
import os

from models import db, migrate
from routes_scan import bp as scan_bp
from routes_cards import bp as cards_bp
from routes_shopify import bp as shopify_bp
from routes_admin import bp as admin_bp
from routes_collection import bp as collection_bp
from routes_auth import bp as auth_bp, init_oauth  # <-- import init_oauth

def _normalize_db_url(url: str | None) -> str:
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url or "sqlite:///local.db"

app = Flask(__name__)

# Config
app.config["SQLALCHEMY_DATABASE_URI"] = _normalize_db_url(os.environ.get("DATABASE_URL"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.environ.get("FLASK_SECRET_KEY", "change_me"))
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"

# CORS
allowed = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
CORS(app, origins=allowed, supports_credentials=True, allow_headers=["Content-Type"],methods=["GET", "POST", "OPTIONS"])

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
init_oauth(app)  # <-- registers 'google' client with this app

# Blueprints
app.register_blueprint(scan_bp)
app.register_blueprint(cards_bp)
app.register_blueprint(shopify_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(collection_bp)


@app.get('/health')
def health():
    return {"ok": True}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5001')), debug=True)
