import { Link, Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import './layout.css'
import HashScroll from './HashScroll'
import Footer from './Footer'
import AuthModal from './AuthModal'
import CartDrawer from './CartDrawer'
import CartIcon from './CartIcon'
import HamburgerMenu from './HamburgerMenu'
import UserMenu from './UserMenu'

// Hook to detect mobile viewport
function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 900)
    }
    
    checkIsMobile()
    window.addEventListener('resize', checkIsMobile)
    return () => window.removeEventListener('resize', checkIsMobile)
  }, [])

  return isMobile
}



type User = { id:string, email:string, name?:string, picture?:string } | null
const API = import.meta.env.VITE_API_BASE_URL || ''

export default function Layout(){
  const [me, setMe] = useState<User>(null)
  const [loading, setLoading] = useState(true)
  const nav = useNavigate()
  const location = useLocation()
  const [showAuth, setShowAuth] = useState(false)
  const isMobile = useIsMobile()

  async function fetchMe(){
    try{
      const authToken = sessionStorage.getItem('auth_token')
      let url = new URL('/api/auth/me', API).toString()
      
      if (authToken) {
        // Send auth token as query parameter instead of header (Safari blocks Authorization header)
        url += `?auth_token=${encodeURIComponent(authToken)}`
        console.log('🔐 Sending auth token as query parameter:', `${authToken.substring(0, 20)}...`)
      } else {
        console.log('❌ No auth token found in sessionStorage')
      }
      
      console.log('🌐 Fetching /api/auth/me with URL:', url)
      const r = await fetch(url, { credentials:'include' })
      const j = await r.json()
      console.log('📥 /api/auth/me response:', j)
      setMe(j.user)
    } finally { setLoading(false) }
  }
  useEffect(()=>{ fetchMe() }, [])

  // Handle auth token from URL hash fragment (for Safari mobile compatibility)
  useEffect(() => {
    // Check both query parameters and hash fragments
    const urlParams = new URLSearchParams(location.search)
    const hashParams = new URLSearchParams(location.hash.substring(1))
    const authToken = urlParams.get('auth_token') || hashParams.get('auth_token')
    
    console.log('🔍 Token extraction debug:', {
      search: location.search,
      hash: location.hash,
      urlParams: Object.fromEntries(urlParams.entries()),
      hashParams: Object.fromEntries(hashParams.entries()),
      authToken: authToken ? `${authToken.substring(0, 20)}...` : null
    })
    
    if (authToken) {
      // Store the auth token in sessionStorage
      sessionStorage.setItem('auth_token', authToken)
      
      // Remove auth_token from URL to clean up the address bar
      const newUrl = new URL(window.location.href)
      newUrl.searchParams.delete('auth_token')
      newUrl.hash = newUrl.hash.replace(/[?&]auth_token=[^&]*/, '').replace(/^#/, '')
      window.history.replaceState({}, '', newUrl.toString())
      
      console.log('🔐 Auth token stored from URL for Safari mobile compatibility:', `${authToken.substring(0, 20)}...`)
      
      // Refresh user data with the new token
      fetchMe()
    }
  }, [location])

  function onSignInClick(){
    setShowAuth(true)            // ⬅️ open modal instead of redirecting
  }

  async function refreshMe(){
    try {
      const authToken = sessionStorage.getItem('auth_token')
      let url = new URL('/api/auth/me', API).toString()
      
      if (authToken) {
        // Send auth token as query parameter instead of header (Safari blocks Authorization header)
        url += `?auth_token=${encodeURIComponent(authToken)}`
      }
      
      const r = await fetch(url, { credentials: 'include' })
      const j = await r.json()
      setMe(j.user || null)
    } catch (error) {
      console.error('Error refreshing user data:', error)
      setMe(null)
    }
  }

  function signInGoogle(){
    const nxt = (import.meta.env.VITE_FRONTEND_PUBLIC_ORIGIN || window.location.origin) + '/'
    window.location.href = new URL(`/api/auth/google/start?next=${encodeURIComponent(nxt)}`, API).toString()
  }
  async function signOut(){
    try {
      const authToken = sessionStorage.getItem('auth_token')
      let url = new URL('/api/auth/logout', API).toString()
      
      if (authToken) {
        // Send auth token as query parameter instead of header (Safari blocks Authorization header)
        url += `?auth_token=${encodeURIComponent(authToken)}`
      }
      
      await fetch(url, { method:'POST', credentials:'include' })
      setMe(null)
      nav('/')
    } catch (error) {
      console.error('Error during logout:', error)
      setMe(null)
      nav('/')
    }
  }

  const hideHeader = location.pathname.startsWith('/cards') || (location.pathname.startsWith('/profile') && isMobile)

  return (
    <div className="app-shell">
      {!hideHeader && (
      <header className="site-nav">
        <div className="container nav-grid">
          {/* left: logo */}
          <Link to="/" className="brand">
            <img src="/assets/logo-titan.svg" alt="TITAN Collectibles" className="brand__logo" />
          </Link>

          {/* center links - only show on desktop */}
          {!isMobile && (
            <nav className="nav-links">
              <Link to="/buy">Shop</Link>
              <a 
                href="#"
                className="nav-link"
                onClick={(e) => {
                  e.preventDefault()
                  if (window.location.pathname !== '/') {
                    nav('/')
                    setTimeout(() => {
                      const aboutEl = document.getElementById('about')
                      if (aboutEl) {
                        aboutEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      }
                    }, 100)
                  } else {
                    const aboutEl = document.getElementById('about')
                    if (aboutEl) {
                      aboutEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                    }
                  }
                }}
              >
                About Us
              </a>
              <a 
                href="#"
                className="nav-link"
                onClick={(e) => {
                  e.preventDefault()
                  if (window.location.pathname !== '/') {
                    nav('/')
                    setTimeout(() => {
                      const contactEl = document.getElementById('contact')
                      if (contactEl) {
                        contactEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      }
                    }, 100)
                  } else {
                    const contactEl = document.getElementById('contact')
                    if (contactEl) {
                      contactEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                    }
                  }
                }}
              >
                Contact
              </a>
            </nav>
          )}

          {/* right actions - desktop nav actions OR mobile hamburger */}
          <div className="nav-actions">
            {!isMobile ? (
              <>
                <CartIcon />
                {loading ? null : me ? (
                    <UserMenu user={me} onSignOut={signOut} />
                    ) : (
                    <button className="btn-outline" onClick={onSignInClick}>Sign In</button>
                  )}
              </>
            ) : (
              <HamburgerMenu 
                me={me} 
                onSignInClick={onSignInClick} 
                onSignOut={signOut} 
              />
            )}
          </div>
        </div>
      </header>
      )}

      <main><HashScroll offset={80}/><Outlet/></main>
      <CartDrawer />
      {!location.pathname.startsWith('/cards') && !location.pathname.startsWith('/profile') && <Footer/>}
      <AuthModal
        open={showAuth}
        onClose={()=>setShowAuth(false)}
        onSignedIn={()=>{ setShowAuth(false); refreshMe() }}
        />
    </div>
    
  )
}
