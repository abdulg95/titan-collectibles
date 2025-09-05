import { Link, Outlet, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import './layout.css'
import HashScroll from './HashScroll'
import Footer from './Footer'
import AuthModal from './AuthModal'
import CartDrawer from './CartDrawer'
import CartIcon from './CartIcon'



type User = { id:string, email:string, name?:string, picture?:string } | null
const API = import.meta.env.VITE_API_BASE_URL || ''

export default function Layout(){
  const [me, setMe] = useState<User>(null)
  const [loading, setLoading] = useState(true)
  const nav = useNavigate()
  const [showAuth, setShowAuth] = useState(false)

  async function fetchMe(){
    try{
      const r = await fetch(new URL('/api/auth/me', API).toString(), { credentials:'include' })
      const j = await r.json()
      setMe(j.user)
    } finally { setLoading(false) }
  }
  useEffect(()=>{ fetchMe() }, [])

  function onSignInClick(){
    setShowAuth(true)            // ⬅️ open modal instead of redirecting
  }

  async function refreshMe(){
    const r = await fetch(new URL('/api/auth/me', API).toString(), { credentials:'include' })
    const j = await r.json()
    setMe(j.user || null)
  }

  function signInGoogle(){
    const nxt = (import.meta.env.VITE_FRONTEND_PUBLIC_ORIGIN || window.location.origin) + '/'
    window.location.href = new URL(`/api/auth/google/start?next=${encodeURIComponent(nxt)}`, API).toString()
  }
  async function signOut(){
    await fetch(new URL('/api/auth/logout', API).toString(), { method:'POST', credentials:'include' })
    setMe(null)
    nav('/')
  }

  return (
    <div className="app-shell">
      <header className="site-nav">
        <div className="container nav-grid">
          {/* left: logo */}
          <Link to="/" className="brand">
            <img src="/assets/logo-titan.svg" alt="TITAN Collectibles" className="brand__logo" />
          </Link>


          {/* center links */}
          <nav className="nav-links">
            <Link to="/buy">Shop</Link>
            <Link to="/#about">About Us</Link>      {/* scrolls to About on home */}
            <Link to="/#contact">Contact</Link>     {/* scrolls to Contact on home */}
          </nav>

          {/* right actions */}
          <div className="nav-actions">
            <CartIcon />
            {loading ? null : me ? (
                <button className="btn-outline" onClick={signOut}>Sign Out</button>
                ) : (
                <button className="btn-outline" onClick={onSignInClick}>Sign In</button>
            )}
          </div>
        </div>
      </header>

      <main><HashScroll offset={80}/><Outlet/></main>
      <CartDrawer />
      <Footer/>
      <AuthModal
        open={showAuth}
        onClose={()=>setShowAuth(false)}
        onSignedIn={()=>{ setShowAuth(false); refreshMe() }}
        />
    </div>
    
  )
}
