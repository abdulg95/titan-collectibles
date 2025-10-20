# backend/routes_auth.py
import os
import re
import uuid
from urllib.parse import urljoin, urlencode, urlparse, parse_qs

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

def _serializer(kind: str = 'email') -> URLSafeTimedSerializer:
    secret = current_app.config["SECRET_KEY"]
    if kind == 'email':
        salt = current_app.config.get("EMAIL_VERIFICATION_SALT", "email-verify")
    elif kind == 'password':
        salt = current_app.config.get("PASSWORD_RESET_SALT", "password-reset")
    else:
        raise ValueError("unknown serializer kind")
    return URLSafeTimedSerializer(secret_key=secret, salt=salt)

def valid_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s or ""))

def _generate_auth_token(user_id):
    """Generate a secure auth token for URL-based authentication"""
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(str(user_id), salt=current_app.config.get('AUTH_TOKEN_SALT', 'auth-token'))

def _verify_auth_token(token):
    """Verify and extract user ID from auth token"""
    try:
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        user_id = serializer.loads(token, salt=current_app.config.get('AUTH_TOKEN_SALT', 'auth-token'), max_age=3600)  # 1 hour expiry
        return user_id
    except (BadSignature, SignatureExpired):
        return None

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
    # Works even if your model doesn't have `name` or `picture`
    return {
        "id": _id_str(u.id),
        "email": u.email,
        "name": getattr(u, "name", None),
        "picture": getattr(u, "picture", None),
        "email_verified": bool(getattr(u, "email_verified", False)),
        "location": getattr(u, "location", None),
        "date_of_birth": getattr(u, "date_of_birth", None),
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
    # Try Authorization header first (for Safari mobile compatibility)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        user_id = _verify_auth_token(token)
        if user_id:
            uid = _uuid(user_id)
            if uid:
                u = db.session.get(User, uid)
                if u:
                    print(f"✅ User found via auth token: {u.email}")
                    return jsonify({"user": user_json(u)})
        print(f"❌ Invalid auth token: {token[:20]}...")
    
    # Fallback to session-based authentication
    sid = session.get("uid")
    print(f"🔍 /me endpoint: sid={sid}, session_id={session.get('_id', 'None')}, user_agent={request.headers.get('User-Agent', 'Unknown')[:50]}...")
    if not sid:
        print("❌ No session ID found")
        return jsonify({"user": None})
    uid = _uuid(sid)
    if not uid:
        print(f"❌ Invalid session ID: {sid}")
        session.clear()
        return jsonify({"user": None})
    u = db.session.get(User, uid)
    if not u:
        print(f"❌ User not found for UID: {uid}")
        session.clear()
        return jsonify({"user": None})
    print(f"✅ User found: {u.email}")
    return jsonify({"user": user_json(u)})

@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})

@bp.route("/update-profile", methods=["POST", "OPTIONS"])
def update_profile():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    current_app.logger.info("Update profile endpoint hit")
    
    sid = session.get("uid")
    if not sid:
        current_app.logger.warning("No session ID found")
        return jsonify({"ok": False, "error": "not_logged_in"}), 401
    
    uid = _uuid(sid)
    if not uid:
        current_app.logger.warning("Invalid session ID: %s", sid)
        session.clear()
        return jsonify({"ok": False, "error": "invalid_session"}), 401
    
    user = db.session.get(User, uid)
    if not user:
        current_app.logger.warning("User not found for ID: %s", uid)
        session.clear()
        return jsonify({"ok": False, "error": "user_not_found"}), 404
    
    data = request.get_json(force=True) or {}
    name = data.get("name")
    current_app.logger.info("Updating name to: %s", name)
    
    if name is not None:
        if hasattr(User, "name"):
            user.name = name.strip() if name.strip() else None
        else:
            current_app.logger.error("Name field not available on User model")
            return jsonify({"ok": False, "error": "name_field_not_available"}), 400
    
    try:
        db.session.commit()
        current_app.logger.info("Profile updated successfully")
        response = jsonify({"ok": True, "user": user_json(user)})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Profile update error: %s", e)
        return jsonify({"ok": False, "error": "update_failed"}), 500

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
    
    # Generate auth token for URL-based authentication (Safari mobile compatibility)
    auth_token = _generate_auth_token(user.id)
    
    print(f"🔐 Google callback: Set session uid={session['uid']}, auth_token={auth_token[:20]}..., user_agent={request.headers.get('User-Agent', 'Unknown')[:50]}...")
    dest = session.pop("post_login_redirect", None) or _frontend_origin()
    
    # Add auth token to redirect URL for Safari mobile compatibility
    dest_url = urlparse(dest)
    query_params = parse_qs(dest_url.query)
    query_params['auth_token'] = [auth_token]
    new_query = urlencode(query_params, doseq=True)
    dest_with_token = f"{dest_url.scheme}://{dest_url.netloc}{dest_url.path}?{new_query}"
    
    return redirect(dest_with_token)

# ---------------- Email + Password ----------------
@bp.post("/signup")
def signup():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = data.get("name") or ""
    location = data.get("location") or ""
    date_of_birth = data.get("date_of_birth")

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
    if hasattr(User, "location"):
        new_kwargs["location"] = location if location else None
    if hasattr(User, "date_of_birth") and date_of_birth:
        from datetime import datetime
        try:
            new_kwargs["date_of_birth"] = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            pass  # Invalid date format, skip

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

    # --- Password reset: request link ---
# --- Password reset: request link ---
@bp.route('/password/forgot', methods=['POST', 'OPTIONS'])
def password_forgot():
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    # Always return ok to avoid user enumeration
    try:
        if email:
            u = User.query.filter_by(email=email).first()
            if u:
                token = _serializer('password').dumps({'uid': _id_str(u.id)})
                reset_url = urljoin(_frontend_origin().rstrip('/') + '/', f"reset-password?{urlencode({'token': token})}")
                html = f"""
                  <p>Hi {getattr(u, 'name', None) or u.email},</p>
                  <p>We received a request to reset your password. Click the link below to set a new one:</p>
                  <p><a href="{reset_url}">Reset your password</a></p>
                  <p>If you didn't request this, you can ignore this email.</p>
                """
                send_email(u.email, "Reset your password", html, f"Open this link: {reset_url}")
    except Exception as e:
        current_app.logger.exception("password_forgot error: %s", e)
    return jsonify({'ok': True})


# --- Password reset: apply new password ---
@bp.route('/password/reset', methods=['POST', 'OPTIONS'])
def password_reset():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.get_json(force=True) or {}
    token = data.get('token') or ''
    new_pw = data.get('password') or ''
    if len(new_pw) < 8:
        return jsonify({'ok': False, 'error': 'weak_password'}), 400

    try:
        payload = _serializer('password').loads(token, max_age=3600*2)  # 2h
    except SignatureExpired:
        return jsonify({'ok': False, 'error': 'token_expired'}), 400
    except BadSignature:
        return jsonify({'ok': False, 'error': 'token_invalid'}), 400

    uid = _uuid(payload.get('uid'))
    if not uid:
        return jsonify({'ok': False, 'error': 'invalid_uid'}), 400

    u = db.session.get(User, uid)
    if not u:
        return jsonify({'ok': False, 'error': 'not_found'}), 404

    # Set new password
    u.set_password(new_pw)

    # ✅ Consider reset as proof of email ownership
    if hasattr(User, 'email_verified') and not getattr(u, 'email_verified', False):
        u.email_verified = True

    db.session.commit()

    # Optionally sign them in after reset
    session['uid'] = _id_str(u.id)
    return jsonify({'ok': True})
