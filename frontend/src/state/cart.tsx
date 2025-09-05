// src/state/cart.tsx
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import {
  ensureCart, getCart, addToCart, updateLineQuantity, removeLine,
  goToCheckout, type CartData, type CartLine,
  getFirstVariantIdByHandle,   // ⬅️ ADD THIS IMPORT
} from '../lib/shopify'

type CartCtx = {
  cart: CartData | null
  isOpen: boolean
  open: () => void
  close: () => void
  totalQty: number
  lines: CartLine[]
  add: (variantId: string, qty?: number) => Promise<void>
  addByHandle: (handle: string, qty?: number) => Promise<void>  // ⬅️ ADD THIS
  inc: (lineId: string) => Promise<void>
  dec: (lineId: string) => Promise<void>
  remove: (lineId: string) => Promise<void>
  reload: () => Promise<void>
  checkout: () => void
}

const Ctx = createContext<CartCtx>(null as any)

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [cart, setCart] = useState<CartData | null>(null)
  const [isOpen, setOpen] = useState(false)

  async function load() {
    const base = await ensureCart()
    const full = await getCart(base.id)   // your current signature, keep it
    if (full) setCart(full)
  }

  useEffect(() => { load() }, [])

  async function add(variantId: string, qty = 1) {
    await addToCart(variantId, qty)
    await load()
    setOpen(true)
  }

  // ⬇️ NEW: add by product handle (fetch first variant, then reuse add)
  async function addByHandle(handle: string, qty = 1) {
    const variantId = await getFirstVariantIdByHandle(handle)
    await add(variantId, qty)
  }

  async function inc(lineId: string) {
    if (!cart) return
    const line = cart.lines.nodes.find(l => l.id === lineId)
    if (!line) return
    await updateLineQuantity(cart.id, lineId, line.quantity + 1)
    await load()
  }

  async function dec(lineId: string) {
    if (!cart) return
    const line = cart.lines.nodes.find(l => l.id === lineId)
    if (!line) return
    const next = Math.max(1, line.quantity - 1)
    await updateLineQuantity(cart.id, lineId, next)
    await load()
  }

  async function removeLineFn(lineId: string) {
    if (!cart) return
    await removeLine(cart.id, lineId)
    await load()
  }

  const value = useMemo<CartCtx>(() => ({
    cart,
    isOpen,
    open: () => setOpen(true),
    close: () => setOpen(false),
    totalQty: cart?.totalQuantity || 0,
    lines: cart?.lines.nodes || [],
    add,
    addByHandle,               // ⬅️ EXPOSE IT
    inc,
    dec,
    remove: removeLineFn,
    reload: load,
    checkout: goToCheckout
  }), [cart, isOpen])

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useCart() { return useContext(Ctx) }
