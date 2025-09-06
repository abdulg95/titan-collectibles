// src/components/AuthModal.tsx
import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import './authmodal.css'
import ForgotView from './ForgotView'

const API = import.meta.env.VITE_API_BASE_URL || ''
const FRONTEND = import.meta.env.VITE_FRONTEND_PUBLIC_ORIGIN || window.location.origin

type Props = {
  open: boolean
  onClose: () => void
  onSignedIn?: (user:any)=>void
}

type View = 'signin' | 'signup' | 'forgot'

export default function AuthModal({ open, onClose, onSignedIn }: Props){
  const loc = useLocation()

  // one state to rule them all
  const [view, setView] = useState<View>('signin')

  // form state (used for signin/signup views)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const emailRef = useRef<HTMLInputElement>(null)

  // prevent background scroll & reset on close
  useEffect(()=>{
    if(open){
      document.body.classList.add('modal-open')
      // focus email for signin/signup; ForgotView handles its own focus
      if (view !== 'forgot') setTimeout(()=>emailRef.current?.focus(), 0)
    } else {
      document.body.classList.remove('modal-open')
      // reset on close
      setView('signin'); setEmail(''); setPassword(''); setErr(null); setBusy(false)
    }
    return ()=>document.body.classList.remove('modal-open')
  }, [open, view])

  // close on ESC
  useEffect(()=>{
    function onKey(e:KeyboardEvent){ if(e.key==='Escape' && open) onClose() }
    window.addEventListener('keydown', onKey)
    return ()=>window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if(!open) return null

  const nextAbs = FRONTEND + loc.pathname + loc.search + loc.hash

  async function signInPassword(e:React.FormEvent){
    e.preventDefault()
    setErr(null); setBusy(true)
    try{
      const r = await fetch(new URL('/api/auth/login', API).toString(), {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        credentials:'include',
        body: JSON.stringify({ email: email.trim().toLowerCase(), password })
      })
      const j = await r.json()
      if(!r.ok){ setErr(j.error || 'invalid_credentials'); return }
      onSignedIn?.(j.user)
      onClose()
    }catch{
      setErr('network_error')
    }finally{ setBusy(false) }
  }

  async function signUpPassword(e:React.FormEvent){
    e.preventDefault()
    setErr(null); setBusy(true)
    try{
      const r = await fetch(new URL('/api/auth/signup', API).toString(), {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        credentials:'include',
        body: JSON.stringify({ email: email.trim().toLowerCase(), password, name: email.split('@')[0] })
      })
      const j = await r.json()
      if(!r.ok){ setErr(j.error || 'signup_failed'); return }
      // backend currently sends { ok, need_verification }, not a user
      // close and let user check their inbox
      onClose()
    }catch{
      setErr('network_error')
    }finally{ setBusy(false) }
  }

  function continueWithGoogle(){
    const url = new URL('/api/auth/google/start', API)
    url.searchParams.set('next', nextAbs)
    window.location.href = url.toString()
  }

  // click outside to close
  function backdropClick(e: React.MouseEvent<HTMLDivElement>){
    if(e.target === e.currentTarget) onClose()
  }

  return (
    <div className="authmodal" role="dialog" aria-modal="true" aria-labelledby="auth-title" onMouseDown={backdropClick}>
      <div className="authpanel" onMouseDown={(e)=>e.stopPropagation()}>
        <button className="auth-close" aria-label="Close" onClick={onClose}>×</button>

        <h2 id="auth-title">
          {view === 'signin' ? 'Sign In' : view === 'signup' ? 'Create account' : 'Forgot password'}
        </h2>

        {view === 'forgot' ? (
          <ForgotView onBack={()=>setView('signin')} />
        ) : (
          <>
            <form onSubmit={view==='signin' ? signInPassword : signUpPassword} className="auth-form">
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

              <label>
                <span>Password</span>
                <div className="pw-wrap">
                  <input
                    type={showPw?'text':'password'}
                    value={password}
                    onChange={e=>setPassword(e.target.value)}
                    placeholder="Your password"
                    required
                    minLength={8}
                  />
                  <button
                    type="button"
                    className="pw-toggle"
                    onClick={()=>setShowPw(s=>!s)}
                    aria-label={showPw ? 'Hide password' : 'Show password'}
                    title={showPw ? 'Hide password' : 'Show password'}
                  >
                    {showPw ? (
                      // eye-off
                      <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M3 3l18 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                        <path d="M10.58 6.08A9.9 9.9 0 0 1 12 6c6 0 10 6 10 6a18.6 18.6 0 0 1-3.05 3.65" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                        <path d="M6.34 7.5A18.1 18.1 0 0 0 2 12s4 6 10 6c1.2 0 2.34-.2 3.4-.56" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                        <path d="M12 9.5a2.5 2.5 0 1 1-2.5 2.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                      </svg>
                    ) : (
                      // eye
                      <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                        <circle cx="12" cy="12" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.6" />
                      </svg>
                    )}
                  </button>
                </div>
              </label>

              {view==='signin' && (
                <div className="row-between" style={{marginTop:8}}>
                  <button
                    type="button"
                    className="link"
                    onClick={()=>setView('forgot')}
                    style={{background:'transparent', border:0, color:'#9fb0c6', cursor:'pointer'}}
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              {err && <div className="error">{err}</div>}

              <button className="btn-primary" disabled={busy || !email || !password}>
                {view==='signin' ? (busy?'Signing in…':'Sign In') : (busy?'Creating…':'Create Account')}
              </button>
            </form>

            <div className="or"><span>OR</span></div>

            <button className="btn-outline social" onClick={continueWithGoogle}>
              <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="" />
              Continue with Google
            </button>

            <p className="switch">
              {view==='signin' ? (
                <>Don’t have an account?{' '}
                  <button className="linklike" onClick={()=>{ setView('signup'); setErr(null) }}>
                    Sign Up
                  </button>
                </>
              ) : (
                <>Already have an account?{' '}
                  <button className="linklike" onClick={()=>{ setView('signin'); setErr(null) }}>
                    Sign In
                  </button>
                </>
              )}
            </p>
          </>
        )}
      </div>
    </div>
  )
}
