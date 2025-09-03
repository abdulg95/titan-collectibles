import { useState } from 'react'
const API = import.meta.env.VITE_API_BASE_URL || ''

export default function SignIn(){
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const [err,setErr] = useState<string | null>(null)

  async function submit(e:any){
    e.preventDefault(); setErr(null)
    try{
      const r = await fetch(new URL('/api/auth/login', API).toString(), {
        method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include',
        body: JSON.stringify({ email, password })
      })
      const j = await r.json()
      if(!r.ok){ setErr(j.error || 'login_failed'); return }
      window.location.href = '/'
    }catch{ setErr('network_error') }
  }

  function signInGoogle(){
    const nxt = window.location.origin + '/'
    window.location.href = new URL(`/api/auth/google/start?next=${encodeURIComponent(nxt)}`, API).toString()
  }

  return (
    <div style={{maxWidth:420, margin:'0 auto', padding:24}}>
      <h1 style={{fontWeight:700, fontSize:22, marginBottom:8}}>Sign in</h1>
      <form onSubmit={submit} style={{display:'grid', gap:10}}>
        <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}
               style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8}} />
        <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)}
               style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8}} />
        {err && <div style={{color:'#b00020', fontSize:13}}>
          {err === 'email_not_verified' ? 'Please verify your email via the link we sent.' : 'Invalid email or password.'}
        </div>}
        <button style={{padding:'10px 12px', borderRadius:8, background:'#000', color:'#fff'}}>Sign in</button>
      </form>

      <div style={{marginTop:16}}>
        <button onClick={signInGoogle} style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8, width:'100%'}}>
          Continue with Google
        </button>
      </div>
    </div>
  )
}
