// src/components/HamburgerMenu.tsx
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useCart } from '../state/cart'
import './hamburger-menu.css'

type User = { id: string, email: string, name?: string, picture?: string } | null

type Props = {
  me: User
  onSignInClick: () => void
  onSignOut: () => void
}

export default function HamburgerMenu({ me, onSignInClick, onSignOut }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const nav = useNavigate()
  const { totalQty, open } = useCart()

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  const closeMenu = () => {
    setIsOpen(false)
  }

  const handleNavClick = (path: string) => {
    closeMenu()
    nav(path)
  }

  const handleScrollToSection = (sectionId: string) => {
    closeMenu()
    if (window.location.pathname !== '/') {
      nav('/')
      setTimeout(() => {
        const element = document.getElementById(sectionId)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    } else {
      const element = document.getElementById(sectionId)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }

  return (
    <div className="hamburger-menu">
      {/* Hamburger Button */}
      <button 
        className={`hamburger-button ${isOpen ? 'open' : ''}`}
        onClick={toggleMenu}
        aria-label="Toggle menu"
      >
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      {/* Overlay */}
      {isOpen && (
        <div className="hamburger-overlay" onClick={closeMenu}></div>
      )}

      {/* Menu Panel */}
      <div className={`hamburger-panel ${isOpen ? 'open' : ''}`}>
        {/* Header with Logo and Close Button */}
        <div className="hamburger-header">
          <Link to="/" className="hamburger-logo" onClick={closeMenu}>
            <img src="/assets/logo-titan.svg" alt="TITAN Collectibles" className="hamburger-logo-img" />
          </Link>
          <button 
            className="hamburger-close"
            onClick={closeMenu}
            aria-label="Close menu"
          >
            ×
          </button>
        </div>
        
        <nav className="hamburger-nav">
          <Link 
            to="/buy" 
            className="hamburger-nav-item"
            onClick={() => handleNavClick('/buy')}
          >
            Shop
          </Link>
          
          <button 
            className="hamburger-nav-item hamburger-nav-button"
            onClick={() => handleScrollToSection('about')}
          >
            About Us
          </button>
          
          <button 
            className="hamburger-nav-item hamburger-nav-button"
            onClick={() => handleScrollToSection('contact')}
          >
            Contact
          </button>

          {/* Cart */}
          <button 
            className="hamburger-nav-item hamburger-nav-button hamburger-cart"
            onClick={() => {
              closeMenu()
              open()
            }}
          >
            Cart {totalQty > 0 && `(${totalQty})`}
          </button>

          {/* Profile - only show when logged in */}
          {me && (
            <Link 
              to="/profile" 
              className="hamburger-nav-item"
              onClick={() => handleNavClick('/profile')}
            >
              Profile
            </Link>
          )}

          <div className="hamburger-nav-divider"></div>

          {/* Auth Section */}
          {me ? (
            <button 
              className="hamburger-nav-item hamburger-nav-button hamburger-signout"
              onClick={() => {
                closeMenu()
                onSignOut()
              }}
            >
              Sign Out
            </button>
          ) : (
            <button 
              className="hamburger-nav-item hamburger-nav-button"
              onClick={() => {
                closeMenu()
                onSignInClick()
              }}
            >
              Sign In
            </button>
          )}
        </nav>
      </div>
    </div>
  )
}