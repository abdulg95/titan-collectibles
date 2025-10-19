import { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'

export default function ScanLanding(){
  const { tagId } = useParams()
  const [sp] = useSearchParams()
  const nav = useNavigate()

  const [phase, setPhase] = useState('loading')   // 'loading' | 'registered'
  const [cardId, setCardId] = useState(null)

  useEffect(()=>{
    const base = import.meta.env.VITE_API_BASE_URL || ''
    const u = new URL('/api/scan/resolve', base)

    if (tagId) u.searchParams.set('tagId', tagId)

    // forward all possible keys we might receive
    ;['enc','eCode','cmac','tt','t','template','templateId'].forEach(k=>{
      const v = sp.get(k)
      if (v) u.searchParams.set(k, v)
    })

    ;(async()=>{
      try {
        const r = await fetch(u.toString(), { credentials:'include' })
        const j = await r.json().catch(()=>null)

        if (!r.ok || !j || j.ok === false) {
          nav('/?scan=fail', { replace:true }); 
          return
        }

        // First-ever scan (warehouse registration)
        if (j.minted) {
          setCardId(j.cardId)
          setPhase('registered')
          return
        }

        // Subsequent scans: always send to card view, which will handle claim UI
        const id = j.cardId
        nav(`/cards/${id}`, { replace:true })
      } catch {
        nav('/?scan=fail', { replace:true })
      }
    })()
  }, [tagId]) // eslint-disable-line react-hooks/exhaustive-deps

  if (phase === 'registered') {
    return (
      <div style={{padding:24, textAlign:'center'}}>
        <h1 style={{margin:'16px 0'}}>Card has been registered</h1>
        {cardId && (
          <p style={{opacity:.8, marginBottom:24}}>
            Serial created and linked to this tag. You can scan again to claim later.
          </p>
        )}
        <div style={{display:'flex', gap:12, justifyContent:'center'}}>
          <button
            onClick={()=>nav('/', { replace:true })}
            style={{
              padding:'10px 16px', borderRadius:8, border:'1px solid #ccc',
              background:'#fff', cursor:'pointer'
            }}
          >
            Done
          </button>
          {cardId && (
            <button
              onClick={()=>nav(`/cards/${cardId}`, { replace:true })}
              style={{
                padding:'10px 16px', borderRadius:8, border:'none',
                background:'#111', color:'#fff', cursor:'pointer'
              }}
            >
              View Card
            </button>
          )}
        </div>
      </div>
    )
  }

  return <p style={{padding:24}}>Verifying tag…</p>
}