import { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'

export default function ScanLanding(){
  const { tagId } = useParams()
  const [sp] = useSearchParams()
  const nav = useNavigate()

  const [phase, setPhase] = useState('loading')   // 'loading' | 'registered'
  const [cardId, setCardId] = useState(null)
  const [error, setError] = useState(null)

  useEffect(()=>{
    const base = import.meta.env.VITE_API_BASE_URL || ''
    
    // Check if this is the new URL format (titansportshq.com/scan?t=000000000002)
    const templateCode = sp.get('t')
    const newTagId = sp.get('id') || tagId
    const encryptedData = sp.get('data')
    
    let apiUrl
    let params = new URLSearchParams()
    
    if (templateCode && encryptedData) {
      // New Titan NFC verification system
      apiUrl = new URL('/api/verification/verify', base)
      params.set('id', newTagId || '')
      params.set('data', encryptedData)
      params.set('t', templateCode)
    } else {
      // Legacy ETRNL system
      apiUrl = new URL('/api/scan/resolve', base)
      if (tagId) params.set('tagId', tagId)
      
      // forward all possible keys we might receive from ETRNL
      ;['enc','eCode','cmac','tt','t','template','templateId'].forEach(k=>{
        const v = sp.get(k)
        if (v) params.set(k, v)
      })
    }

    const fullUrl = `${apiUrl.toString()}?${params.toString()}`

    ;(async()=>{
      try {
        console.log('Verifying with URL:', fullUrl)
        const r = await fetch(fullUrl, { credentials:'include' })
        const j = await r.json().catch(()=>null)

        if (!r.ok || !j || j.ok === false) {
          console.error('Verification failed:', j)
          setError(j.reason || 'Verification failed')
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
      } catch (err) {
        console.error('Verification error:', err)
        setError('Network error during verification')
      }
    })()
  }, [tagId, sp, nav]) // eslint-disable-line react-hooks/exhaustive-deps

  if (error) {
    return (
      <div style={{padding:24, textAlign:'center'}}>
        <h1 style={{margin:'16px 0', color:'#d32f2f'}}>Verification Failed</h1>
        <p style={{opacity:.8, marginBottom:24}}>
          {error}
        </p>
        <div style={{display:'flex', gap:12, justifyContent:'center'}}>
          <button
            onClick={()=>nav('/', { replace:true })}
            style={{
              padding:'10px 16px', borderRadius:8, border:'1px solid #ccc',
              background:'#fff', cursor:'pointer'
            }}
          >
            Go Home
          </button>
          <button
            onClick={()=>window.location.reload()}
            style={{
              padding:'10px 16px', borderRadius:8, border:'none',
              background:'#111', color:'#fff', cursor:'pointer'
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

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