// src/components/CartDrawer.tsx
import { useEffect, useMemo, useState } from 'react'
import { useCart } from '../state/cart'
import { getProductByHandle } from '../lib/shopify'
import './cart.css'

const ADDON_HANDLE = 'card-sleeve' // e.g. "protective-sleeves"

type Money = { amount: string; currencyCode: string }

export default function CartDrawer(){
  const { isOpen, close, lines, cart, inc, dec, remove, add, checkout } = useCart()
  const money = (m?: Money) =>
    m ? new Intl.NumberFormat(undefined, { style:'currency', currency:m.currencyCode }).format(Number(m.amount)) : ''

  // Per-line spinners
  const [plusPending, setPlusPending] = useState<Record<string, boolean>>({})
  const [minusPending, setMinusPending] = useState<Record<string, boolean>>({})
  const setPlus = (id: string, on: boolean) =>
    setPlusPending(p => on ? { ...p, [id]: true } : ( () => { const { [id]:_, ...r } = p; return r })())
  const setMinus = (id: string, on: boolean) =>
    setMinusPending(p => on ? { ...p, [id]: true } : ( () => { const { [id]:_, ...r } = p; return r })())

  async function onPlus(lineId: string){ setPlus(lineId, true);  try{ await inc(lineId) } finally{ setPlus(lineId, false) } }
  async function onMinus(lineId: string){ setMinus(lineId, true); try{ await dec(lineId) }  finally{ setMinus(lineId, false) } }

  // Checkout spinner
  const [checkoutBusy, setCheckoutBusy] = useState(false)

  // ----- Add-on product -----
  const [addon, setAddon] = useState<{
    variantId: string
    title: string
    image: string
    price: Money
  } | null>(null)
  const [addonPlusBusy, setAddonPlusBusy] = useState(false)
  const [addonMinusBusy, setAddonMinusBusy] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function loadAddon(){
      if (!ADDON_HANDLE) return
      try{
        const p = await getProductByHandle(ADDON_HANDLE)
        if (!p) return
        const v = p.variants?.nodes?.[0]
        const img = p.images?.nodes?.[0]?.url || ''
        
        // Only show add-on if variant exists, is available for sale, and has stock
        // quantityAvailable can be null if inventory is not tracked, so check both
        // If quantityAvailable is 0 or negative, don't show it
        const qty = v?.quantityAvailable
        const hasStock = qty === null || qty === undefined || qty > 0
        
        if (!v?.id || !v?.availableForSale || !hasStock) return
        
        if (!cancelled){
          setAddon({ variantId: v.id, title: p.title, image: img, price: v.price })
        }
      } catch (e) {
        console.error('Error loading add-on:', e)
      }
    }
    loadAddon()
    return () => { cancelled = true }
  }, [])

  // find if add-on already in cart
  const addonLine = useMemo(() => {
    if (!addon) return null
    return lines.find(l => l.merchandise.id === addon.variantId) || null
  }, [addon, lines])

  async function onAddonInc(){
    setAddonPlusBusy(true)
    try{
      if (addonLine) await inc(addonLine.id)
      else if (addon) await add(addon.variantId, 1)
    } finally { setAddonPlusBusy(false) }
  }
  async function onAddonDec(){
    if (!addonLine) return
    setAddonMinusBusy(true)
    try{
      if (addonLine.quantity <= 1) await remove(addonLine.id)
      else await dec(addonLine.id)
    } finally { setAddonMinusBusy(false) }
  }

  return (
    <div className={`cart-drawer ${isOpen ? 'open' : ''}`}>
      <div className="cart-panel">
        <div className="cart-head">
          <h3>Your Cart</h3>
          <button className="x" onClick={close} aria-label="Close">✕</button>
        </div>

        <div className="cart-lines">
          {lines.length === 0 && <p className="empty">Your cart is empty.</p>}
          {lines.map(l => {
            const img = l.merchandise.product.images.nodes[0]?.url || l.merchandise.image?.url || ''
            const title = l.merchandise.product.title
            const price = l.merchandise.price
            const busyPlus = !!plusPending[l.id]
            const busyMinus = !!minusPending[l.id]
            return (
              <div className="line" key={l.id}>
                <img src={img} alt={title} />
                <div className="meta">
                  <div className="cd-title">{title}</div>
                  <div className="cd-price">{money(price)}</div>
                  <div className="cd-qty">
                    <button onClick={()=>onMinus(l.id)} aria-label="Decrease" disabled={busyMinus}>
                      {busyMinus ? <span className="btn-spinner" /> : '−'}
                    </button>
                    <span className="cd-qty-num">{l.quantity}</span>
                    <button onClick={()=>onPlus(l.id)} aria-label="Increase" disabled={busyPlus}>
                      {busyPlus ? <span className="btn-spinner" /> : '+'}
                    </button>
                  </div>
                </div>
                <button className="rm" onClick={()=>remove(l.id)} aria-label="Remove">Remove</button>
              </div>
            )
          })}
        </div>

        {/* ---- Add-ons section ---- */}
        {addon && (
          <div className="cart-addons">
            <div className="addons-head">Add-ons</div>
            <div className="addon-item">
              <img className="addon-img" src={addon.image} alt={addon.title} />
              <div className="addon-meta">
                <div className="addon-title">{addon.title}</div>
                <div className="addon-price">{money(addon.price)}</div>
              </div>
              <div className="addon-qty">
                <button onClick={onAddonDec} aria-label="Decrease" disabled={addonMinusBusy || !addonLine}>
                  {addonMinusBusy ? <span className="btn-spinner" /> : '−'}
                </button>
                <span className="addon-qty-num">{addonLine?.quantity ?? 0}</span>
                <button onClick={onAddonInc} aria-label="Increase" disabled={addonPlusBusy}>
                  {addonPlusBusy ? <span className="btn-spinner" /> : '+'}
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="cart-foot">
          <div className="row">
            <span>Subtotal</span>
            <strong>{money(cart?.cost.subtotalAmount)}</strong>
          </div>
          <button
            className="checkout"
            disabled={checkoutBusy || !cart?.checkoutUrl}
            onClick={() => { setCheckoutBusy(true); checkout() }}
          >
            {checkoutBusy ? <span className="btn-spinner btn-spinner--lg" /> : 'Checkout'}
          </button>
          <button className="continue" onClick={close}>Continue shopping</button>
        </div>
      </div>
      <div className="overlay" onClick={close} />
    </div>
  )
}
