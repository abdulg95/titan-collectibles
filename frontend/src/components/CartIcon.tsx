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
      <svg
        className="cart-svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        role="img"
        focusable="false"
        aria-hidden="true"
      >
        <circle cx="9" cy="21" r="1" />
        <circle cx="20" cy="21" r="1" />
        <path d="M1 1h4l2.68 12.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
      </svg>

      {totalQty > 0 && <span className="cart-badge">{totalQty}</span>}
    </button>
  )
}
