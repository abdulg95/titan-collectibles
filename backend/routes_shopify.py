from flask import Blueprint, request, abort
import hmac, hashlib, base64, os

bp = Blueprint('shopify_webhooks', __name__, url_prefix='/webhooks/shopify')
SHARED_SECRET = os.environ.get('SHOPIFY_WEBHOOK_SECRET','')

def verify_hmac(req):
    digest = hmac.new(SHARED_SECRET.encode(), msg=req.data, digestmod=hashlib.sha256).digest()
    calc = base64.b64encode(digest).decode()
    return hmac.compare_digest(calc, req.headers.get('X-Shopify-Hmac-Sha256',''))

@bp.post('/orders_create')
def orders_create():
    if not verify_hmac(request): abort(401)
    # TODO: store order payload, link to cart attributes
    return ('',200)
