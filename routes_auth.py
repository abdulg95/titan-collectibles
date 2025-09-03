# backend/routes_auth.py
from flask import Blueprint, request, jsonify, session, redirect
from authlib.integrations.flask_client import OAuth
from urllib.parse import urljoin, urlencode
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from models import db, User   # <-- absolute import
import os, re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# OAuth registry (we init & register in init_oauth(app))
oauth = OAuth()

def init_oauth(app):
    """Initialize Authlib and register the Google client."""
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

def get_oauth_client():
    client = oauth.create_client('google')
    if not client:
        raise RuntimeError("OAuth is not initialized. Call init_oauth(app) in app.py before registering this blueprint.")
    return client

def _frontend_origin() -> str:
    return os.getenv('FRONTEND_ORIGIN', '/') or '/'

def _backend_base() -> str:
    return os.getenv('BACKEND_PUBLIC_URL') or os.getenv('OAUTH_REDIRECT_BASE') or request.host_url.rstrip('/')

def _redirect_uri():
    base = os.getenv('OAUTH_REDIRECT_BASE', request.host_url.rstrip('/'))
    return urljoin(base + '/', 'api/auth/google/callback')

def _serializer():
    return URLSafeTimedSerializer(
        secret_key=os.getenv('SECRET_KEY', 'dev'),
        salt=os.getenv('EMAIL_VERIFICATION_SALT', 'email-verify')
    )

# mail helper (console fallback if you don't have mailer.py)
try:
    from mailer import send_email  # absolute import
except Exception:
    def send_email(to: str, subject: str, html: str, text: str | None = None):
        print("\n=== EMAIL (console) ===")
        print("To:", to)
        print("Subject:", subject)
        print("Text:", text or "")
        print("HTML:\n", html)
        print("=======================\n")
        return True

def valid_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s or ""))

# -------- Session helpers --------
@bp.get('/me')
def me():
    uid = session.get('uid')
    if not uid:
        return jsonify({'user': None})
    u = User.query.get(uid)
    if not u:
        session.clear()
        return jsonify({'user': None})
    return jsonify({'user': {'id': u.id, 'email': u.email, 'name': u.name, 'picture': u.picture}})

@bp.post('/logout')
def logout():
    session.clear()
    return jsonify({'ok': True})

# -------- Google OAuth --------
@bp.get('/google/start')
def google_start():
    nxt = request.args.get('next') or _frontend_origin()
    session['post_login_redirect'] = nxt
    client = get_oauth_client()
    return client.authorize_redirect(redirect_uri=_redirect_uri(), prompt='select_account')

@bp.get('/google/callback')
def google_cb():
    client = get_oauth_client()
    try:
        # 1) Exchange code -> tokens
        token = client.authorize_access_token()

        # 2) Call the absolute userinfo endpoint (from server metadata if available)
        metadata = getattr(client, 'server_metadata', None) or {}
        userinfo_url = metadata.get('userinfo_endpoint', 'https://openidconnect.googleapis.com/v1/userinfo')

        resp = client.get(userinfo_url)
        resp.raise_for_status()
        info = resp.json()
    except Exception as e:
        from flask import current_app
        current_app.logger.exception("Google callback error: %s", e)
        return redirect(_frontend_origin() + '/?login=fail')


    # Extract fields
    sub = (info.get('sub') or '').strip()
    email = (info.get('email') or '').lower().strip()
    name = info.get('name') or ''
    picture = info.get('picture') or ''
    email_verified = bool(info.get('email_verified'))

    if not sub or not email:
        return redirect(_frontend_origin() + '/?login=fail')

    # Link by google_sub; else by email; else create
    user = User.query.filter_by(google_sub=sub).first()
    if not user:
        user = User.query.filter_by(email=email).first()
        if user:
            user.google_sub = sub
            if email_verified:
                user.email_verified = True
        else:
            user = User(
                google_sub=sub,
                email=email,
                name=name,
                picture=picture,
                email_verified=True if email_verified else False
            )
            db.session.add(user)

    # keep profile fresh
    user.name = name or user.name
    user.picture = picture or user.picture
    db.session.commit()

    session['uid'] = user.id
    dest = session.pop('post_login_redirect', None) or _frontend_origin()
    return redirect(dest)


# -------- Email+Password --------
@bp.post('/signup')
def signup():
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    name = data.get('name') or ''

    if not valid_email(email):
        return jsonify({'ok': False, 'error': 'invalid_email'}), 400
    if len(password) < 8:
        return jsonify({'ok': False, 'error': 'weak_password'}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'ok': False, 'error': 'email_in_use'}), 409

    u = User(email=email, name=name, email_verified=False)
    u.set_password(password)
    db.session.add(u); db.session.commit()

    token = _serializer().dumps({'uid': u.id})
    verify_url = urljoin(_backend_base() + '/', f"api/auth/verify-email?{urlencode({'token': token})}")
    html = f"""
      <p>Hi {u.name or u.email},</p>
      <p>Confirm your email to activate your account:</p>
      <p><a href="{verify_url}">Verify your email</a></p>
      <p>If you didn’t sign up, you can ignore this message.</p>
    """
    send_email(u.email, "Verify your email", html, f"Open this link to verify: {verify_url}")

    session.clear()
    return jsonify({'ok': True, 'need_verification': True})

@bp.post('/login')
def login_password():
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    u = User.query.filter_by(email=email).first()
    if not u or not u.check_password(password):
        return jsonify({'ok': False, 'error': 'invalid_credentials'}), 401
    if not u.email_verified:
        return jsonify({'ok': False, 'error': 'email_not_verified'}), 403

    session['uid'] = u.id
    return jsonify({'ok': True, 'user': {'id': u.id, 'email': u.email, 'name': u.name}})

# -------- Email Verification --------
@bp.get('/verify-email')
def verify_email():
    token = request.args.get('token') or ''
    try:
        data = _serializer().loads(token, max_age=86400)
    except SignatureExpired:
        return jsonify({'ok': False, 'error': 'token_expired'}), 400
    except BadSignature:
        return jsonify({'ok': False, 'error': 'token_invalid'}), 400

    uid = data.get('uid')
    u = User.query.get(uid)
    if not u:
        return jsonify({'ok': False, 'error': 'not_found'}), 404

    if not u.email_verified:
        u.email_verified = True
        db.session.commit()

    session['uid'] = u.id
    return redirect(_frontend_origin() + '/?verify=ok')

@bp.post('/verify/resend')
def verify_resend():
    data = request.get_json(force=True) or {}
    email = (data.get('email') or '').strip().lower()
    if not valid_email(email):
        return jsonify({'ok': True})

    u = User.query.filter_by(email=email).first()
    if not u or u.email_verified:
        return jsonify({'ok': True})

    token = _serializer().dumps({'uid': u.id})
    verify_url = urljoin(_backend_base() + '/', f"api/auth/verify-email?{urlencode({'token': token})}")
    html = f"""
      <p>Hi {u.name or u.email},</p>
      <p>Confirm your email to activate your account:</p>
      <p><a href="{verify_url}">Verify your email</a></p>
    """
    send_email(u.email, "Verify your email", html, f"Open this link to verify: {verify_url}")
    return jsonify({'ok': True})
