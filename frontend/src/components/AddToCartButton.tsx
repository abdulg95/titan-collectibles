// src/components/AddToCartButton.tsx
import { useState } from 'react'
import { useCart } from '../state/cart'

type Props = {
  handle?: string
  variantId?: string
  style?: 'primary' | 'pill'
  quantity?: number
  onAdded?: (qtyInCart: number) => void
}

export default function AddToCartButton({
  handle, variantId, style = 'primary', quantity = 1, onAdded
}: Props) {
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const { add, addByHandle, reload, cart } = useCart()

  async function onClick(){
    try{
      setErr(null); setBusy(true)
      if (variantId) await add(variantId, quantity)
      else if (handle) await addByHandle(handle, quantity)
      else throw new Error('Provide variantId or handle')

      await reload()
      onAdded?.(cart?.totalQuantity ?? 0)
    }catch(e:any){
      setErr(e.message || 'Add to cart failed')
    }finally{
      setBusy(false)
    }
  }

  return (
    <div>
      <button className={style === 'pill' ? 'pill-btn' : 'btn-primary'} disabled={busy} onClick={onClick}>
        {busy ? 'Adding…' : 'Add to Cart'}
      </button>
      {err && <div style={{ color: '#f88', marginTop: 8, fontSize: 12 }}>{err}</div>}
    </div>
  )
}
