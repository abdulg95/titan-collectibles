import { Link } from 'react-router-dom'
import './footer.css'

export default function Footer(){
  return (
    <footer className="site-footer">
      <div className="container foot-row">
        <div className="foot-left">
          <div className="foot-brand">
            <img src="/assets/logo-titan.svg" alt="TITAN" className="foot-logo" />
            <span className="foot-sub">COLLECTIBLES</span>
          </div>
        </div>

        <nav className="foot-links">
          <Link to="/#about">About</Link>
          <Link to="/terms">Terms of Use</Link>
          <Link to="/privacy">Privacy</Link> 
          <Link to="/#contact">Contact</Link>
          {/* Optional: add Privacy when ready -> <Link to="/privacy">Privacy</Link> */}
        </nav>

        <div className="foot-right">
          <a href="https://www.instagram.com/titansportshq?igsh=MXh2N2Qyb2tvMXk1cw==" target="_blank" rel="noreferrer" aria-label="Instagram" className="ig">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Z" stroke="currentColor" strokeWidth="1.4"/>
              <circle cx="12" cy="12" r="3.5" stroke="currentColor" strokeWidth="1.4"/>
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>
            </svg>
          </a>
        </div>
      </div>

      <div className="container foot-bottom">
        <small>© {new Date().getFullYear()} Titan Sports and Collectibles Inc. All rights reserved.</small>
      </div>
    </footer>
  )
}
