import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_BASE_URL || ''

export default function ResetPassword(){
  const [sp] = useSearchParams()
  const nav = useNavigate()
  const token = sp.get('token') || ''
  const [pw, setPw] = useState('')
  const [pw2, setPw2] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(()=>{
    if(!token) setErr('Missing token. Please use the link from your email.')
  }, [token])

  async function submit(e: React.FormEvent){
    e.preventDefault()
    setErr(null); setMsg(null)
    if(pw.length < 8) return setErr('Password must be at least 8 characters.')
    if(pw !== pw2) return setErr('Passwords do not match.')
    setBusy(true)
    try{
      const r = await fetch(new URL('/api/auth/password/reset', API).toString(), {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        credentials: 'include',
        body: JSON.stringify({ token, password: pw })
      })
      const j = await r.json()
      if(!r.ok || !j.ok){
        throw new Error(j?.error || 'Reset failed')
      }
      setMsg('Password updated. Redirecting…')
      setTimeout(()=> nav('/'), 1200)
    }catch(e:any){
      setErr(e.message || 'Something went wrong')
    }finally{ setBusy(false) }
  }

  return (
    <div className="container" style={{maxWidth: 480, padding: '40px 16px'}}>
      <h2>Reset your password</h2>
      <p style={{opacity:.8, marginTop:6}}>Enter a new password for your account.</p>

      {err && <div style={{color:'#f88', marginTop:10}}>{err}</div>}
      {msg && <div style={{color:'#8f8', marginTop:10}}>{msg}</div>}

      <form onSubmit={submit} style={{display:'grid', gap:12, marginTop:14}}>
        <label>New password
          <input type="password" value={pw} onChange={e=>setPw(e.target.value)} required/>
        </label>
        <label>Confirm password
          <input type="password" value={pw2} onChange={e=>setPw2(e.target.value)} required/>
        </label>
        <button className="btn-primary" disabled={busy || !token}>
          {busy ? 'Updating…' : 'Update password'}
        </button>
      </form>
    </div>
  )
}
