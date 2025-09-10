// src/pages/CardView.tsx
import { useEffect, useState } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'

type CardResponse = {
  id: string
  owned: boolean
  ownedByMe: boolean
  serial_no: number
  template: {
    athlete: {
      full_name: string | null
      sport: string | null
    }
    glb_url: string | null
    version: string | null
  }
}

export default function CardView() {
  const { cardId } = useParams()
  const [sp] = useSearchParams()
  const isClaim = sp.get('claim') === '1'

  // If claim flow is not ready, show “coming soon” immediately.
  if (isClaim) return <ClaimComingSoon />

  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [card, setCard] = useState<CardResponse | null>(null)

  useEffect(() => {
    let canceled = false
    async function go() {
      setLoading(true); setErr(null)
      try {
        const base = import.meta.env.VITE_API_BASE_URL || ''
        const url = new URL(`/api/cards/${cardId}`, base)
        const r = await fetch(url.toString(), { credentials: 'include' })
        if (!r.ok) throw new Error(`Card ${r.status}`)
        const j: CardResponse = await r.json()
        if (!canceled) setCard(j)
      } catch (e: any) {
        if (!canceled) setErr(e?.message || 'Failed to load card')
      } finally {
        if (!canceled) setLoading(false)
      }
    }
    if (cardId) go()
    return () => { canceled = true }
  }, [cardId])

  if (loading) return <div className="card-loading">Loading…</div>
  if (err)     return <div className="card-error">Error: {err}</div>
  if (!card)   return <div className="card-error">Card not found.</div>

  return (
    <main className="card-page">
      <h1>Card #{card.serial_no}</h1>
      <p>
        {card.template?.athlete?.full_name || 'Athlete'} — {card.template?.athlete?.sport || ''}
      </p>
      {/* …rest of your card UI… */}
    </main>
  )
}

function ClaimComingSoon() {
  return (
    <main className="claim-soon">
      <div className="claim-soon__box">
        <h1>Digital experience will be available soon</h1>
        <p>
          You’ve successfully scanned a registered card. The full digital
          experience for this card is not live yet. Check back shortly.
        </p>
        <div className="claim-actions">
          <Link to="/" className="claim-btn">Return Home</Link>
          <a
            className="claim-btn claim-btn--ghost"
            href="https://instagram.com/titansportshq"
            target="_blank" rel="noreferrer"
          >
            Follow updates
          </a>
        </div>
      </div>
    </main>
  )
}