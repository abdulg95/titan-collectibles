// src/components/ForgotView.tsx
import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'

const API = import.meta.env.VITE_API_BASE_URL || ''

type Props = {
  onBack: () => void
  onReset?: () => void
  /** If you already have a token (e.g. passed from modal), you can supply it here. */
  tokenFromProps?: string
}

type Stage = 'request' | 'sent' | 'reset' | 'done'

export default function ForgotView({ onBack, onReset, tokenFromProps }: Props){
  const loc = useLocation()
  const qs = new URLSearchParams(loc.search)
  const tokenInUrl = qs.get('token') || ''
  const token = tokenFromProps || tokenInUrl

  const [stage, setStage] = useState<Stage>(token ? 'reset' : 'request')
  const [email, setEmail] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string|null>(null)

  const [pw1, setPw1] = useState('')
  const [pw2, setPw2] = useState('')
  const [show1, setShow1] = useState(false)
  const [show2, setShow2] = useState(false)

  const emailRef = useRef<HTMLInputElement>(null)
  const pwRef = useRef<HTMLInputElement>(null)

  useEffect(()=>{
    if(stage==='request') setTimeout(()=>emailRef.current?.focus(), 0)
    if(stage==='reset') setTimeout(()=>pwRef.current?.focus(), 0)
  }, [stage])

  async function submitRequest(e:React.FormEvent){
    e.preventDefault()
    setErr(null); setBusy(true)
    try{
      const r = await fetch(new URL('/api/auth/password/forgot', API).toString(), {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        credentials:'include',
        body: JSON.stringify({ email: email.trim().toLowerCase() })
      })
      const j = await r.json().catch(()=> ({}))
      if(!r.ok){ setErr(j.error || 'request_failed'); return }
      setStage('sent')
    }catch{
      setErr('network_error')
    }finally{ setBusy(false) }
  }

  const pwValid = pw1.length >= 8 && pw1 === pw2

  async function submitReset(e:React.FormEvent){
    e.preventDefault()
    setErr(null); setBusy(true)
    try{
      const r = await fetch(new URL('/api/auth/password/reset', API).toString(), {
        method:'POST',
        headers:{ 'Content-Type':'application/json' },
        credentials:'include',
        body: JSON.stringify({ token, password: pw1 })
      })
      const j = await r.json().catch(()=> ({}))
      if(!r.ok){ setErr(j.error || 'reset_failed'); return }
      setStage('done')
      onReset?.()
    }catch{
      setErr('network_error')
    }finally{ setBusy(false) }
  }

  return (
    <div>
      {stage==='request' && (
        <form onSubmit={submitRequest} className="auth-form">
          <p style={{marginTop:0, color:'#9fb0c6'}}>
            Enter your email and we’ll send you a reset link.
          </p>

          <label>
            <span>Email</span>
            <input
              ref={emailRef}
              type="email"
              value={email}
              onChange={e=>setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>

          {err && <div className="error">{err}</div>}

          <button className="btn-primary" disabled={busy || !email}>
            {busy ? 'Sending…' : 'Send reset link'}
          </button>

          <button
            type="button"
            className="linklike"
            onClick={onBack}
            style={{marginTop:10}}
          >
            Back to sign in
          </button>
        </form>
      )}

      {stage==='sent' && (
        <div className="auth-form">
          <p>We’ve sent a link to <strong>{email}</strong> if it’s associated with an account.</p>
          <p>Open it on this device to continue.</p>
          <div style={{display:'flex', gap:8}}>
            <button className="btn-primary" onClick={onBack}>Back to sign in</button>
            <button className="btn-outline" onClick={()=>{ setStage('request'); setErr(null); }}>
              Send again
            </button>
          </div>
        </div>
      )}

      {stage==='reset' && (
        <form onSubmit={submitReset} className="auth-form">
          <p style={{marginTop:0, color:'#9fb0c6'}}>Choose a new password.</p>

          <label>
            <span>New password</span>
            <div className="pw-wrap">
              <input
                ref={pwRef}
                type={show1 ? 'text' : 'password'}
                value={pw1}
                onChange={e=>setPw1(e.target.value)}
                placeholder="At least 8 characters"
                required
                minLength={8}
              />
              <button
                type="button"
                className="pw-toggle"
                onClick={()=>setShow1(s=>!s)}
                aria-label={show1 ? 'Hide password' : 'Show password'}
              >
                {show1 ? eyeOffSvg() : eyeSvg()}
              </button>
            </div>
          </label>

          <label>
            <span>Confirm password</span>
            <div className="pw-wrap">
              <input
                type={show2 ? 'text' : 'password'}
                value={pw2}
                onChange={e=>setPw2(e.target.value)}
                required
                minLength={8}
              />
              <button
                type="button"
                className="pw-toggle"
                onClick={()=>setShow2(s=>!s)}
                aria-label={show2 ? 'Hide password' : 'Show password'}
              >
                {show2 ? eyeOffSvg() : eyeSvg()}
              </button>
            </div>
          </label>

          {/* inline validation */}
          {!pwValid && (pw1 || pw2) && (
            <div className="error">
              {pw1.length < 8 ? 'Password must be at least 8 characters' : 'Passwords do not match'}
            </div>
          )}
          {err && <div className="error">{err}</div>}

          <button className="btn-primary" disabled={busy || !pwValid}>
            {busy ? 'Saving…' : 'Save new password'}
          </button>

          {!token && (
            <p className="switch" style={{marginTop:10}}>
              Don’t have a token? Check your email for the reset link.
            </p>
          )}
        </form>
      )}

      {stage==='done' && (
        <div className="auth-form">
          <p>Your password has been updated.</p>
          <button className="btn-primary" onClick={onBack}>Return to sign in</button>
        </div>
      )}
    </div>
  )
}

/* ---- icons (same style as AuthModal) ---- */
function eyeSvg(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  )
}
function eyeOffSvg(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 3l18 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <path d="M10.58 6.08A9.9 9.9 0 0 1 12 6c6 0 10 6 10 6a18.6 18.6 0 0 1-3.05 3.65" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <path d="M6.34 7.5A18.1 18.1 0 0 0 2 12s4 6 10 6c1.2 0 2.34-.2 3.4-.56" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
      <path d="M12 9.5a2.5 2.5 0 1 1-2.5 2.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
    </svg>
  )
}
