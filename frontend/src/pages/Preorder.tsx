import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import './preorder.css'

import {
  getProductByHandle,
  addToCart,
  ensureCart,
  getCheckoutUrl,
  getCart as fetchCartById,
  updateLineQuantity,
  removeLine,
  type Money,
  type CartLine,
} from '../lib/shopify'

// Hardcoded handles
const PACK_HANDLE  = 'series-1-card-pack'
const ADDON_HANDLE = 'card-sleeve'

export default function PreorderPage() {
  const logoSrc = '/assets/logo-titan.svg'
  const waLogo  = '/assets/world-archery.png'
  const packImgFallback = '/assets/pack-placeholder.png'

  // modal state
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>('')

  // Shopify products
  const [pack, setPack] = useState<{ variantId:string; title:string; image:string; price:Money } | null>(null)
  const [addon, setAddon] = useState<{ variantId:string; title:string; image:string; price:Money } | null>(null)

  // Cart state
  const [cartId, setCartId] = useState<string | null>(null)
  const [cartLines, setCartLines] = useState<CartLine[]>([])
  const [cartSubtotal, setCartSubtotal] = useState<Money | null>(null)
  const [cartCount, setCartCount] = useState<number>(0)

  // Load products & ensure cart once
  useEffect(() => {
    let cancel = false
    ;(async () => {
      try {
        const c = await ensureCart().catch(() => null)
        if (!cancel && c?.id) setCartId(c.id)

        const p1 = await getProductByHandle(PACK_HANDLE).catch(() => null)
        if (p1 && !cancel) {
          const v = p1.variants?.nodes?.[0]
          const img = p1.images?.nodes?.[0]?.url || ''
          if (v?.id) setPack({ variantId: v.id, title: p1.title, image: img, price: v.price })
        }

        const p2 = await getProductByHandle(ADDON_HANDLE).catch(() => null)
        if (p2 && !cancel) {
          const v = p2.variants?.nodes?.[0]
          const img = p2.images?.nodes?.[0]?.url || ''
          if (v?.id) setAddon({ variantId: v.id, title: p2.title, image: img, price: v.price })
        }
      } catch {/* ignore */}
    })()
    return () => { cancel = true }
  }, [])

  // Refresh cart view
  async function refreshCart(id?: string | null) {
    const cid = id ?? cartId
    if (!cid) return
    const c = await fetchCartById(cid).catch(() => null)
    setCartLines(c?.lines?.nodes ?? [])
    setCartSubtotal(c?.cost?.subtotalAmount ?? null)
    setCartCount(c?.totalQuantity ?? 0)
  }

  // When modal opens, pull latest cart
  useEffect(() => { if (open) refreshCart() }, [open]) // eslint-disable-line

  const money = (m?: Money) =>
    m ? new Intl.NumberFormat(undefined, { style:'currency', currency:m.currencyCode }).format(Number(m.amount)) : ''

  const packImg = useMemo(() => pack?.image || packImgFallback, [pack])

  // Helpers to find current qty for our two SKUs
  function findLine(variantId?: string) {
    if (!variantId) return null
    return cartLines.find(l => l.merchandise.id === variantId) || null
  }
  const packLine  = findLine(pack?.variantId)
  const addonLine = findLine(addon?.variantId)
  const packQty   = packLine?.quantity ?? 0
  const addonQty  = addonLine?.quantity ?? 0

  // Single-place quantity editor (adds/removes/updates actual cart lines)
  async function setVariantQty(variantId: string, nextQty: number) {
    if (!cartId) return
    const line = cartLines.find(l => l.merchandise.id === variantId) || null
    if (line) {
      if (nextQty <= 0) await removeLine(cartId, line.id).catch(()=>{})
      else await updateLineQuantity(cartId, line.id, nextQty).catch(()=>{})
    } else {
      if (nextQty > 0) await addToCart(variantId, nextQty).catch(()=>{})
    }
    await refreshCart()
  }

  async function handleCheckout() {
    setBusy(true); setError('')
    try {
      const url = await getCheckoutUrl()
      if (!url) throw new Error('No checkout URL')
      window.location.href = url
    } catch (e:any) {
      setError(e?.message || 'Something went wrong.')
    } finally {
      setBusy(false)
    }
  }

  // Filter out our two items from “other items” list
  const otherLines = cartLines.filter(l =>
    l.merchandise.id !== pack?.variantId && l.merchandise.id !== addon?.variantId
  )

  return (
    <main className="preorder-hero">
      {/* TITAN logo */}
      <img src={logoSrc} alt="TITAN" className="titan-logo" width={179} height={47.895} aria-hidden="true" />

      {/* Left column */}
      <section className="hero-content">
        <h1 className="hero-title">Series One: A New Era.</h1>

        <p className="hero-copy">
          Tap your card to reveal exclusive athlete stories, stats, and gear insights — powered by NFC.
          Collect all 8 cards featuring the sport’s top athletes to unlock the bonus 9th.
        </p>

        <div className="button-row">
          <button
            type="button"
            className="cta"
            onClick={() => setOpen(true)}
            title={!pack ? 'Loading product…' : undefined}
          >
            Pre-order
          </button>
        </div>

        <div className="partner">
          <img src={waLogo} alt="World Archery — Officially Licensed Collectibles" />
          <small>Officially Licensed Collectibles</small>
        </div>
      </section>

      {/* Right column */}
      <aside className="pack-wrap">
        <img src={packImg} alt="Titan Series One pack" className="pack-img" width={321} height={504} />
      </aside>

      {/* Footer */}
      <footer className="preorder-footer">
        <div className="footer-left">
          <div className="brand-row">
            <img src={logoSrc} alt="TITAN" width="92" height="20" />
            <a href="https://instagram.com/titansportshq" aria-label="Instagram" className="ig" target="_blank" rel="noreferrer">
              <svg className="ig-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Z" stroke="currentColor" strokeWidth="1.4"/>
                <circle cx="12" cy="12" r="3.5" stroke="currentColor" strokeWidth="1.4"/>
                <circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>
              </svg>
            </a>
          </div>
          <div className="legal">© {new Date().getFullYear()} Titan Sports and Collectibles Inc. All rights reserved.</div>
        </div>
      </footer>

      {/* Modal */}
      {open && createPortal(
        <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="preorder-title" onClick={() => setOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 id="preorder-title">Pre-order Titan Series One</h2>
            <p className="modal-copy">Set quantities here, then go straight to checkout.</p>

            {/* SINGLE PLACE to edit packs & sleeves */}
            <div className="line-items">
              {/* Card Pack row */}
              <div className="line-item">
                <img className="thumb" src={pack?.image || packImgFallback} alt={pack?.title || 'Card Pack'} />
                <div className="meta">
                  <div className="ti">{pack?.title || 'Card Pack'}</div>
                  {pack?.price && <div className="sub">{money(pack.price)}</div>}
                </div>
                <div className="cartline-ctrls">
                  <button className="qty-btn" onClick={() => pack?.variantId && setVariantQty(pack.variantId, Math.max(0, packQty - 1))} aria-label="Decrease" disabled={!pack}>
                    −
                  </button>
                  <span className="qty-pill">× {packQty}</span>
                  <button className="qty-btn" onClick={() => pack?.variantId && setVariantQty(pack.variantId, packQty + 1)} aria-label="Increase" disabled={!pack}>
                    +
                  </button>
                  {packQty > 0 && pack?.variantId && (
                    <button
                        className="icon-btn rm-line"
                        onClick={() => setVariantQty(pack.variantId!, 0)}
                        aria-label="Remove card pack"
                        title="Remove"
                    >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
                            aria-hidden="true" width="16" height="16">
                        <path d="M3 6h18"/>
                        <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                        <path d="M10 11v6M14 11v6"/>
                        </svg>
                    </button>
                    )}
                </div>
              </div>

              {/* Sleeve row */}
              {addon && (
                <div className="line-item">
                  <img className="thumb" src={addon.image} alt={addon.title} />
                  <div className="meta">
                    <div className="ti">{addon.title}</div>
                    <div className="sub">{money(addon.price)}</div>
                  </div>
                  <div className="cartline-ctrls">
                    <button className="qty-btn" onClick={() => setVariantQty(addon.variantId, Math.max(0, addonQty - 1))} aria-label="Decrease">−</button>
                    <span className="qty-pill">× {addonQty}</span>
                    <button className="qty-btn" onClick={() => setVariantQty(addon.variantId, addonQty + 1)} aria-label="Increase">+</button>
                    {addonQty > 0 && (
                        <button
                            className="icon-btn rm-line"
                            onClick={() => setVariantQty(addon.variantId, 0)}
                            aria-label="Remove sleeve add-on"
                            title="Remove"
                        >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
                                aria-hidden="true" width="16" height="16">
                            <path d="M3 6h18"/>
                            <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                            <path d="M10 11v6M14 11v6"/>
                            </svg>
                        </button>
                    )}
                  </div>
                </div>
              )}

              {/* Other items (from earlier tests) — remove only to keep UI simple */}
              {otherLines.length > 0 && (
                <>
                  <div className="sub" style={{opacity:.85, marginTop:4}}>Other items in your cart</div>
                  {otherLines.map(l => {
                    const img = l.merchandise.product.images.nodes[0]?.url || l.merchandise.image?.url || ''
                    const title = l.merchandise.product.title
                    const price = l.merchandise.price
                    return (
                      <div className="line-item" key={l.id}>
                        <img className="thumb" src={img} alt={title} />
                        <div className="meta">
                          <div className="ti">{title}</div>
                          <div className="sub">{money(price)} · ×{l.quantity}</div>
                        </div>
                        <div className="cartline-ctrls">
                        <button
                        className="icon-btn rm-line"
                        onClick={() => removeLine(cartId!, l.id).then(()=>refreshCart())}
                        aria-label={`Remove ${title}`}
                        title="Remove"
                        >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"
                            aria-hidden="true" width="16" height="16">
                            <path d="M3 6h18"/>
                            <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                            <path d="M10 11v6M14 11v6"/>
                        </svg>
                        </button>
                        </div>
                      </div>
                    )
                  })}
                </>
              )}

              <div className="line-total" style={{marginTop:6}}>
                <span>Cart subtotal</span>
                <strong>{money(cartSubtotal || undefined)}</strong>
              </div>
            </div>

            {error && <div className="modal-error">{error}</div>}

            <div className="modal-actions">
              <button className="btn-secondary" onClick={() => setOpen(false)} disabled={busy}>Cancel</button>
              <button className="cta" onClick={handleCheckout} disabled={busy || (!pack && !addon)}>
                {busy ? 'Starting checkout…' : 'Checkout'}
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </main>
  )
}