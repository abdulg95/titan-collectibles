// src/components/UserMenu.tsx
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './usermenu.css'

type User = { 
  id: string
  email: string
  name?: string
  picture?: string
}

type Props = {
  user: User
  onSignOut: () => void
}

export default function UserMenu({ user, onSignOut }: Props) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  // Debug: Log user data to see what we're working with
  console.log('UserMenu received user:', user)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleProfileClick = () => {
    navigate('/profile')
    setIsOpen(false)
  }

  const handleSignOut = () => {
    onSignOut()
    setIsOpen(false)
  }

  return (
    <div className="user-menu" ref={dropdownRef}>
      <button 
        className="user-menu-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="User menu"
      >
        <img 
          src={user.picture || "/assets/default-avatar.jpg"} 
          alt="Profile" 
          className="user-avatar"
          onLoad={() => console.log('Profile image loaded successfully:', user.picture)}
          onError={(e) => {
            console.log('Profile image failed to load:', user.picture)
            console.log('Error event:', e)
            e.currentTarget.src = "/assets/default-avatar.jpg"
          }}
        />
        <svg 
          className={`dropdown-arrow ${isOpen ? 'open' : ''}`}
          width="12" 
          height="8" 
          viewBox="0 0 12 8" 
          fill="none"
        >
          <path 
            d="M1 1.5L6 6.5L11 1.5" 
            stroke="currentColor" 
            strokeWidth="1.5" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="user-dropdown">
          <div className="user-info">
            <img 
              src={user.picture || "/assets/default-avatar.jpg"} 
              alt="Profile" 
              className="dropdown-avatar"
              onLoad={() => console.log('Dropdown profile image loaded successfully:', user.picture)}
              onError={(e) => {
                console.log('Dropdown profile image failed to load:', user.picture)
                console.log('Error event:', e)
                e.currentTarget.src = "/assets/default-avatar.jpg"
              }}
            />
            <div className="user-details">
              <div className="user-name">{user.name || user.email}</div>
              <div className="user-email">{user.email}</div>
            </div>
          </div>
          
          <div className="dropdown-divider"></div>
          
          <div className="dropdown-menu">
            <button 
              className="dropdown-item"
              onClick={handleProfileClick}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path 
                  d="M8 8C10.2091 8 12 6.20914 12 4C12 1.79086 10.2091 0 8 0C5.79086 0 4 1.79086 4 4C4 6.20914 5.79086 8 8 8Z" 
                  fill="currentColor"
                />
                <path 
                  d="M8 10C3.58172 10 0 13.5817 0 18H16C16 13.5817 12.4183 10 8 10Z" 
                  fill="currentColor"
                />
              </svg>
              Profile
            </button>
            
            <button 
              className="dropdown-item"
              onClick={handleSignOut}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path 
                  d="M6 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V3.33333C2 2.97971 2.14048 2.64057 2.39052 2.39052C2.64057 2.14048 2.97971 2 3.33333 2H6" 
                  stroke="currentColor" 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
                <path 
                  d="M10 11L14 7L10 3" 
                  stroke="currentColor" 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
                <path 
                  d="M14 7H6" 
                  stroke="currentColor" 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}