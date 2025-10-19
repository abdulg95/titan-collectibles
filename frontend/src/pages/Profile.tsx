// src/pages/Profile.tsx
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import HamburgerMenu from '../components/HamburgerMenu'
import './profile.css'

type CollectionItem = {
  id: string
  serial_no: number
  status: string
  template: {
    version: string
    image_url: string
    glb_url: string
  }
  athlete: {
    id: string
    full_name: string
    slug: string
    card_image_url: string
    card_number: number
    series_number: number
  }
}

type User = { 
  id: string
  email: string
  name?: string
  picture?: string
  location?: string
  date_of_birth?: string
}

const API = import.meta.env.VITE_API_BASE_URL || ''

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

export default function Profile() {
  const [items, setItems] = useState<CollectionItem[] | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const isMobile = useIsMobile()
  const [isEditingName, setIsEditingName] = useState(false)
  const [editedName, setEditedName] = useState('')

  const handleEditName = () => {
    setIsEditingName(true)
    setEditedName(user?.name || user?.email || '')
  }

  const handleSaveName = async () => {
    if (!user || !editedName.trim()) return
    
    try {
      console.log('Saving name:', editedName.trim())
      const url = new URL('/api/auth/update-profile', API).toString()
      console.log('API URL:', url)
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ name: editedName.trim() })
      })
      
      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      if (response.ok) {
        const result = await response.json()
        console.log('Update result:', result)
        
        // Update the user state with the new data from backend
        if (result.user) {
          setUser(result.user)
        } else {
          // Fallback to local update if backend doesn't return user data
          setUser({ ...user, name: editedName.trim() })
        }
        
        // Refresh user data to ensure we have the latest information
        await refreshUserData()
        
        setIsEditingName(false)
      } else {
        const errorText = await response.text()
        console.error('Failed to update name:', response.status, errorText)
      }
    } catch (error) {
      console.error('Error updating name:', error)
    }
  }

  const handleCancelEdit = () => {
    setIsEditingName(false)
    setEditedName('')
  }

  const refreshUserData = async () => {
    try {
      const response = await fetch(new URL('/api/auth/me', API).toString(), { 
        credentials: 'include' 
      })
      if (response.ok) {
        const result = await response.json()
        if (result.user) {
          setUser(result.user)
        }
      }
    } catch (error) {
      console.error('Error refreshing user data:', error)
    }
  }

  useEffect(() => {
    fetch(new URL('/api/collection', API).toString(), { credentials: 'include' })
      .then(r => (r.ok ? r.json() : Promise.reject(r)))
      .then(j => setItems(j.items || []))
      .catch(() => {
        setErr('Failed to load collection')
        setItems([])
      })
  }, [])

  useEffect(() => {
    fetch(new URL('/api/auth/me', API).toString(), { credentials: 'include' })
      .then(r => (r.ok ? r.json() : Promise.reject(r)))
      .then(j => setUser(j.user || null))
      .catch(() => setUser(null))
  }, [])

  // Loading (no background card)
  if (items === null) {
    return (
      <main className="collection">
        <h1 className="collection__title">My collection</h1>
        <div className="skeleton title" />
        <div className="skeleton line" />
        <div className="skeleton art" />
        <div className="skeleton button" />
      </main>
    )
  }

  // Empty state (plain background)
  if (items.length === 0) {
    return (
      <div className="collection-page">
        {/* Mobile Header */}
        {isMobile && (
          <header className="collection-header">
            <div className="collection-header-content">
              <Link to="/" className="collection-logo">
                <img src="/assets/logo-titan.svg" alt="TITAN Collectibles" className="collection-logo-img" />
              </Link>
              <HamburgerMenu
                me={user}
                onSignInClick={() => navigate('/signin')}
                onSignOut={() => {
                  fetch(new URL('/api/auth/signout', API).toString(), { 
                    method: 'POST', 
                    credentials: 'include' 
                  }).then(() => {
                    setUser(null)
                    navigate('/')
                  })
                }}
              />
            </div>
          </header>
        )}

        <main className="collection">
          <h1 className="collection__title">My collection</h1>

          <p className="collection__sub">
            No cards in your collection yet. Tap a card to add it here.
          </p>

          {/* If your image is in /public, use src="/assets/collection-empty.png" */}
          <img
            src="/assets/collection-empty.png"
            alt=""
            className="collection__art"
          />

          {/* Profile Section */}
          {user && (
            <div className="profile-section">
              <div className="profile-info">
                <img 
                  src={user.picture || "/assets/default-avatar.jpg"} 
                  alt="Profile" 
                  className="profile-avatar" 
                />
                <div className="profile-details">
                  <h2 className="profile-name">{user.name || user.email}</h2>
                  <p className="profile-email">{user.email}</p>
                </div>
              </div>
            </div>
          )}

          <p className="collection__fine">
            If you're missing digital cards, please <Link to="/">contact us</Link>.
          </p>

          {err && <p className="collection__error">{err}</p>}
        </main>
      </div>
    )
  }

  // Create a map of collected cards by card number
  // Prioritize diamond versions over regular versions
  const collectedCards = new Map<number, CollectionItem>()
  items.forEach(item => {
    if (item.athlete.card_number) {
      const existingCard = collectedCards.get(item.athlete.card_number)
      
      if (!existingCard) {
        // No card yet, add this one
        collectedCards.set(item.athlete.card_number, item)
      } else if (item.template.version === 'diamond' && existingCard.template.version === 'regular') {
        // Replace regular with diamond
        collectedCards.set(item.athlete.card_number, item)
      }
      // If existing is diamond and new is regular, keep the diamond (do nothing)
    }
  })


  // Generate all 9 card slots (001-009)
  const cardSlots = Array.from({ length: 9 }, (_, index) => {
    const cardNumber = index + 1
    const collectedCard = collectedCards.get(cardNumber)
    
    return {
      cardNumber,
      collectedCard
    }
  })


  return (
    <div className="collection-page">
      {/* Mobile Header */}
      {isMobile && (
        <header className="collection-header">
          <div className="collection-header-content">
            <Link to="/" className="collection-logo">
              <img src="/assets/logo-titan.svg" alt="TITAN Collectibles" className="collection-logo-img" />
            </Link>
            <HamburgerMenu
              me={user}
              onSignInClick={() => navigate('/signin')}
              onSignOut={() => {
                fetch(new URL('/api/auth/signout', API).toString(), { 
                  method: 'POST', 
                  credentials: 'include' 
                }).then(() => {
                  setUser(null)
                  navigate('/')
                })
              }}
            />
          </div>
        </header>
      )}

      <main className="collection">
        <h1 className="collection__title">My collection</h1>
        
        <div className="collection-grid">
        {cardSlots.map(({ cardNumber, collectedCard }) => (
          <div key={cardNumber} className="collection-slot">
            {collectedCard ? (
              <Link 
                to={`/cards/${collectedCard.id}`}
                className="collection-card"
              >
                <img 
                  src={collectedCard.template.image_url} 
                  alt={`${collectedCard.athlete.full_name} card`}
                  className="collection-card-image"
                />
              </Link>
            ) : (
              <div className="collection-empty-slot">
                <span className="collection-empty-number">
                  {cardNumber === 9 ? '?' : cardNumber.toString().padStart(3, '0')}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Profile Header */}
      {user && (
        <div className="profile-header">
          <img 
            src={user.picture || "/assets/default-avatar.jpg"} 
            alt="Profile" 
            className="profile-avatar" 
          />
          <div className="profile-details">
            {isEditingName ? (
              <div className="profile-name-edit">
                <input
                  type="text"
                  value={editedName}
                  onChange={(e) => setEditedName(e.target.value)}
                  className="profile-name-input"
                  autoFocus
                />
                <div className="profile-name-actions">
                  <button 
                    className="profile-save-btn"
                    onClick={handleSaveName}
                    disabled={!editedName.trim()}
                  >
                    ✓
                  </button>
                  <button 
                    className="profile-cancel-btn"
                    onClick={handleCancelEdit}
                  >
                    ✕
                  </button>
                </div>
              </div>
            ) : (
              <div className="profile-name-display">
                <h2 className="profile-name">{user.name || user.email}</h2>
                <button 
                  className="profile-edit-btn"
                  onClick={handleEditName}
                  aria-label="Edit name"
                >
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M17.2109 4.17188L15.1367 2.10938L16.3203 0.9375C16.918 0.351562 17.5625 0.304688 18.0898 0.832031L18.4883 1.23047C19.0273 1.76953 18.9922 2.41406 18.3945 3.01172L17.2109 4.17188ZM3.39453 17.9531L0.6875 18.9961C0.40625 19.1133 0.101562 18.7852 0.21875 18.5039L1.33203 15.8906L14.1289 3.11719L16.1797 5.17969L3.39453 17.9531Z" fill="white"/>
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Personal Information Card */}
      {user && (
        <div className="personal-info-card">
          <h3 className="personal-info-title">Personal Information</h3>
          
          <div className="personal-info-section">
            <div className="personal-info-field">
              <div className="personal-info-label">Email</div>
              <div className="personal-info-value">{user.email}</div>
            </div>

            {user.location && (
              <div className="personal-info-field">
                <div className="personal-info-label">Location</div>
                <div className="personal-info-value">{user.location}</div>
              </div>
            )}

            {user.date_of_birth && (
              <div className="personal-info-field">
                <div className="personal-info-label">Date of birth</div>
                <div className="personal-info-value">
                  {new Date(user.date_of_birth).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {err && <p className="collection__error">{err}</p>}
    </main>
    </div>
  )
}

