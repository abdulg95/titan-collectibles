import { useState } from 'react'
const API = import.meta.env.VITE_API_BASE_URL || ''

export default function SignUp(){
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const [name,setName] = useState('')
  const [err,setErr] = useState<string | null>(null)
  const [ok,setOk] = useState(false)

  async function submit(e:any){
    e.preventDefault(); setErr(null)
    try{
      const r = await fetch(new URL('/api/auth/signup', API).toString(), {
        method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include',
        body: JSON.stringify({ email, password, name })
      })
      const j = await r.json()
      if(!r.ok){ setErr(j.error || 'signup_failed'); return }
      // email verification flow returns {need_verification:true}
      setOk(true)
    }catch{ setErr('network_error') }
  }

  function signInGoogle(){
    const nxt = window.location.origin + '/'
    window.location.href = new URL(`/api/auth/google/start?next=${encodeURIComponent(nxt)}`, API).toString()
  }

  if(ok) return (
    <div style={{maxWidth:420, margin:'0 auto', padding:24}}>
      <h1 style={{fontWeight:700, fontSize:22, marginBottom:8}}>Check your email</h1>
      <p>We’ve sent a verification link to <b>{email}</b>. Click it to activate your account.</p>
      <p style={{marginTop:12, fontSize:12, color:'#666'}}>Didn’t get it? Check spam or try again later.</p>
    </div>
  )

  return (
    <div style={{maxWidth:420, margin:'0 auto', padding:24}}>
      <h1 style={{fontWeight:700, fontSize:22, marginBottom:8}}>Create account</h1>
      <form onSubmit={submit} style={{display:'grid', gap:10}}>
        <input placeholder="Name" value={name} onChange={e=>setName(e.target.value)}
               style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8}} />
        <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}
               style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8}} />
        <input type="password" placeholder="Password (min 8)" value={password} onChange={e=>setPassword(e.target.value)}
               style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8}} />
        {err && <div style={{color:'#b00020', fontSize:13}}>{err}</div>}
        <button style={{padding:'10px 12px', borderRadius:8, background:'#000', color:'#fff'}}>Sign up</button>
      </form>

      <div style={{marginTop:16}}>
        <button onClick={signInGoogle} style={{padding:'10px 12px', border:'1px solid #ddd', borderRadius:8, width:'100%'}}>
          Continue with Google
        </button>
      </div>
    </div>
  )
}
