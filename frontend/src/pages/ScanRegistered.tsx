// src/pages/ScanRegistered.tsx
import { useMemo } from 'react'
import { useLocation, Link, useNavigate } from 'react-router-dom'

export default function ScanRegistered() {
  const nav = useNavigate()
  const cardId = new URLSearchParams(useLocation().search).get('card') || ''

  return (
    <div style={{ padding: 24, maxWidth: 540, margin: '0 auto', textAlign: 'center' }}>
      <div style={{
        display:'inline-flex', alignItems:'center', justifyContent:'center',
        width:72, height:72, borderRadius:36, background:'#16a34a20', marginBottom:16
      }}>
        <span style={{ fontSize: 36 }}>✅</span>
      </div>
      <h1 style={{ margin: '8px 0' }}>Card has been registered</h1>
      <p style={{ opacity: .8, marginBottom: 24 }}>
        You can scan the next tag now. This card is ready for the customer to claim.
      </p>

      <div style={{ display:'flex', gap:12, justifyContent:'center' }}>
        <Link
          to={`/cards/${cardId}`}
          style={{ padding:'10px 16px', borderRadius:8, border:'1px solid #ddd', textDecoration:'none' }}
        >
          View card
        </Link>
        <button
          onClick={() => nav(-1)}
          style={{ padding:'10px 16px', borderRadius:8 }}
        >
          Scan next
        </button>
      </div>
    </div>
  )
}