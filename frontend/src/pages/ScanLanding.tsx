import { useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'

export default function ScanLanding(){
  const { tagId } = useParams()
  const [sp] = useSearchParams()
  const nav = useNavigate()

  useEffect(()=>{
    const base = import.meta.env.VITE_API_BASE_URL || ''
    const u = new URL('/api/scan/resolve', base)
    u.searchParams.set('tagId', tagId||'')
    ;['enc','eCode','cmac','tt','t'].forEach(k=>{ const v=sp.get(k); if(v) u.searchParams.set(k,v) })
    ;(async()=>{
      const r = await fetch(u.toString(), { credentials:'include' })
      const j = await r.json()
      if(!j.ok) { nav('/?scan=fail', { replace:true }); return }
      const cardId = j.cardId
      if(j.state === 'unclaimed') nav(`/cards/${cardId}?claim=1`, { replace:true })
      else nav(`/cards/${cardId}`, { replace:true })
    })()
  }, [tagId])

  return <p style={{padding:24}}>Verifying tag…</p>
}
