# backend/routes_auth.py
import os
import re
import uuid
from urllib.parse import urljoin, urlencode

from flask import Blueprint, request, jsonify, session, redirect, current_app
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from models import db, User  # absolute import to match your app layout

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ---------------- OAuth registry ----------------
oauth = OAuth()

def init_oauth(app):
    """Initialize Authlib and register the Google client."""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

def get_oauth_client():
    client = oauth.create_client("google")
    if not client:
        raise RuntimeError(
            "OAuth is not initialized. Call init_oauth(app) in app.py before registering this blueprint."
        )
    return client

# ---------------- helpers ----------------
def _frontend_origin() -> str:
    return os.getenv("FRONTEND_ORIGIN", "/") or "/"

def _backend_base() -> str:
    return os.getenv("BACKEND_PUBLIC_URL") or os.getenv("OAUTH_REDIRECT_BASE") or request.host_url.rstrip("/")

def _redirect_uri() -> str:
    base = os.getenv("OAUTH_REDIRECT_BASE", request.host_url.rstrip("/"))
    return urljoin(base + "/", "api/auth/google/callback")

def _serializer() -> URLSafeTimedSerializer:
    secret = current_app.config["SECRET_KEY"]
    salt = current_app.config.get("EMAIL_VERIFICATION_SALT", "email-verify")
    return URLSafeTimedSerializer(secret_key=secret, salt=salt)

def valid_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s or ""))

def _id_str(val) -> str:
    """Always return a plain string for IDs; prefer hex (no dashes)."""
    if isinstance(val, uuid.UUID):
        return val.hex
    try:
        return uuid.UUID(str(val)).hex
    except Exception:
        return str(val)

def _uuid(val) -> uuid.UUID | None:
    """Parse hex or dashed UUID string into uuid.UUID; return None on failure."""
    try:
        return uuid.UUID(str(val))
    except Exception:
        return None

def user_json(u: User) -> dict:
    # Works even if your model doesn’t have `name` or `picture`
    return {
        "id": _id_str(u.id),
        "email": u.email,
        "name": getattr(u, "name", None),
        "picture": getattr(u, "picture", None),
        "email_verified": bool(getattr(u, "email_verified", False)),
    }

# ---------------- mail helper ----------------
try:
    from mailer import send_email  # your real mailer (SendGrid/SMTP)
except Exception:
    def send_email(to: str, subject: str, html: str, text: str | None = None):
        # console fallback
        print("\n=== EMAIL (console) ===")
        print("To:", to)
        print("Subject:", subject)
        print("Text:", text or "")
        print("HTML:\n", html)
        print("=======================\n")
        return True

# ---------------- session endpoints ----------------
@bp.get("/me")
def me():
    sid = session.get("uid")
    if not sid:
        return jsonify({"user": None})
    uid = _uuid(sid)
    if not uid:
        session.clear()
        return jsonify({"user": None})
    u = db.session.get(User, uid)
    if not u:
        session.clear()
        return jsonify({"user": None})
    return jsonify({"user": user_json(u)})

@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

# ---------------- Google OAuth ----------------
@bp.get("/google/start")
def google_start():
    nxt = request.args.get("next") or _frontend_origin()
    session["post_login_redirect"] = nxt
    client = get_oauth_client()
    return client.authorize_redirect(redirect_uri=_redirect_uri(), prompt="select_account")

@bp.get("/google/callback")
def google_cb():
    client = get_oauth_client()
    try:
        token = client.authorize_access_token()

        # userinfo endpoint (from discovery doc)
        metadata = getattr(client, "server_metadata", None) or {}
        userinfo_url = metadata.get("userinfo_endpoint", "https://openidconnect.googleapis.com/v1/userinfo")

        resp = client.get(userinfo_url)
        resp.raise_for_status()
        info = resp.json()
    except Exception as e:
        current_app.logger.exception("Google callback error: %s", e)
        return redirect(_frontend_origin() + "/?login=fail")

    sub = (info.get("sub") or "").strip()
    email = (info.get("email") or "").lower().strip()
    name = info.get("name") or ""
    picture = info.get("picture") or ""
    email_verified = bool(info.get("email_verified"))

    if not sub or not email:
        return redirect(_frontend_origin() + "/?login=fail")

    # Link by google_sub; else by email; else create
    user = User.query.filter_by(google_sub=sub).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_sub = sub
            if email_verified:
                user.email_verified = True
        else:
            # Build kwargs only for columns that exist on your model
            new_kwargs = {
                "google_sub": sub,
                "email": email,
                "email_verified": bool(email_verified),
            }
            if hasattr(User, "name"):
                new_kwargs["name"] = name
            if hasattr(User, "picture"):
                new_kwargs["picture"] = picture
            user = User(**new_kwargs)
            db.session.add(user)

    # keep profile fresh if columns exist
    if hasattr(User, "name") and name:
        user.name = name
    if hasattr(User, "picture") and picture:
        user.picture = picture

    db.session.commit()

    session["uid"] = _id_str(user.id)
    dest = session.pop("post_login_redirect", None) or _frontend_origin()
    return redirect(dest)

# ---------------- Email + Password ----------------
@bp.post("/signup")
def signup():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = data.get("name") or ""

    if not valid_email(email):
        return jsonify({"ok": False, "error": "invalid_email"}), 400
    if len(password) < 8:
        return jsonify({"ok": False, "error": "weak_password"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"ok": False, "error": "email_in_use"}), 409

    # Only pass supported kwargs to the model
    new_kwargs = {"email": email, "email_verified": False}
    if hasattr(User, "name"):
        new_kwargs["name"] = name

    u = User(**new_kwargs)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    # JSON-safe token (string id)
    token = _serializer().dumps({"uid": _id_str(u.id)})

    # Clear session (optional) or keep a pending uid; we’ll clear for safety
    session.clear()

    verify_url = urljoin(
        _backend_base() + "/",
        f"api/auth/verify-email?{urlencode({'token': token})}",
    )
    html = f"""
      <p>Hi {getattr(u, 'name', None) or u.email},</p>
      <p>Confirm your email to activate your account:</p>
      <p><a href="{verify_url}">Verify your email</a></p>
      <p>If you didn’t sign up, you can ignore this message.</p>
    """
    send_email(u.email, "Verify your email", html, f"Open this link to verify: {verify_url}")

    return jsonify({"ok": True, "need_verification": True})

@bp.post("/login")
def login_password():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify({"ok": False, "error": "invalid_credentials"}), 401
    if not getattr(u, "email_verified", False):
        return jsonify({"ok": False, "error": "email_not_verified"}), 403

    session["uid"] = _id_str(u.id)
    return jsonify({"ok": True, "user": user_json(u)})

# ---------------- Email Verification ----------------
@bp.get("/verify-email")
def verify_email():
    token = request.args.get("token") or ""
    try:
        data = _serializer().loads(token, max_age=86400)  # 24h
    except SignatureExpired:
        return jsonify({"ok": False, "error": "token_expired"}), 400
    except BadSignature:
        return jsonify({"ok": False, "error": "token_invalid"}), 400

    uid = _uuid(data.get("uid"))
    if not uid:
        return jsonify({"ok": False, "error": "invalid_uid"}), 400

    u = db.session.get(User, uid)
    if not u:
        return jsonify({"ok": False, "error": "not_found"}), 404

    if not getattr(u, "email_verified", False):
        u.email_verified = True
        db.session.commit()

    session["uid"] = _id_str(u.id)
    return redirect(_frontend_origin() + "/?verify=ok")

@bp.post("/verify/resend")
def verify_resend():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not valid_email(email):
        return jsonify({"ok": True})

    u = User.query.filter_by(email=email).first()
    if not u or getattr(u, "email_verified", False):
        return jsonify({"ok": True})

    token = _serializer().dumps({"uid": _id_str(u.id)})
    verify_url = urljoin(
        _backend_base() + "/",
        f"api/auth/verify-email?{urlencode({'token': token})}",
    )
    html = f"""
      <p>Hi {getattr(u, 'name', None) or u.email},</p>
      <p>Confirm your email to activate your account:</p>
      <p><a href="{verify_url}">Verify your email</a></p>
    """
    send_email(u.email, "Verify your email", html, f"Open this link to verify: {verify_url}")
    return jsonify({"ok": True})
