// src/components/CartIcon.tsx
import { useCart } from '../state/cart'

export default function CartIcon() {
  const { totalQty, open } = useCart()

  return (
    <button
      className="cart-btn cart-btn--icon"
      onClick={open}
      aria-label="Open cart"
    >
      <img
        src="/assets/cart.png"
        alt="Cart"
        className="cart-img"
        width="24"
        height="24"
      />

      {totalQty > 0 && <span className="cart-badge">{totalQty}</span>}
    </button>
  )
}
