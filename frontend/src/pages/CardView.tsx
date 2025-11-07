// src/pages/CardView.tsx
import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import ClaimModal from '../components/ClaimModal'
import './cardview.css'

type Achievement = {
  title: string
  result: string
  medal: string
  display_order: number
  notes: string | null
}

type Equipment = {
  category: string
  brand: string | null
  model: string | null
  display_order: number
}

type Qualification = {
  year: number
  score: number | null
  event: string | null
}

type Stats = {
  win_percentage: number | null
  average_arrow: number | null
  tiebreak_win_rate: number | null
}

type CardResponse = {
  id: string
  owned: boolean
  ownedByMe: boolean
  serial_no: number
  status: string
  template: {
    athlete: {
      full_name: string | null
      sport: string | null
      discipline: string | null
      dob: string | null
      nationality: string | null
      hometown: string | null
      handedness: string | null
      world_ranking: number | null
      best_world_ranking: number | null
      intl_debut_year: number | null
      bio_short: string | null
      bio_long: string | null
      quote_text: string | null
      quote_source: string | null
      card_image_url: string | null
      card_back_url: string | null
      hero_image_url: string | null
      video_url: string | null
      quote_photo_url: string | null
      action_photo_url: string | null
      qualification_image_url: string | null
      achievements: Achievement[]
      equipment: Equipment[]
      qualifications: Qualification[]
      stats: Stats
      socials: { [key: string]: string }
      sponsors: Array<{ name: string; logo_url: string; url?: string }>
    }
    image_url: string | null
    glb_url: string | null
    version: string | null
  }
}

// Helper function to determine achievement icon
const ASSET_VERSION = '20251107'

const getAchievementIcon = (achievement: Achievement) => {
  // Check if notes field contains special icon type or sequence
  if (achievement.notes && achievement.notes.includes(',')) {
    // Handle sequences (e.g., "trophy,silver", "gold,silver,bronze")
    return 'sequence'
  } else if (achievement.notes === 'trophy') {
    return `/assets/achievements/trophy.png?v=${ASSET_VERSION}`
  } else if (achievement.notes === 'award') {
    return `/assets/achievements/award.png?v=${ASSET_VERSION}`
  }
  
  // Default to medal type
  switch (achievement.medal) {
    case 'gold':
      return `/assets/achievements/gold-medal.png?v=${ASSET_VERSION}`
    case 'silver':
      return `/assets/achievements/silver-medal.png?v=${ASSET_VERSION}`
    case 'bronze':
      return `/assets/achievements/bronze-medal.png?v=${ASSET_VERSION}`
    default:
      return `/assets/achievements/gold-medal.png?v=${ASSET_VERSION}`
  }
}

// Helper function to render medal sequence
const renderMedalSequence = (sequence: string) => {
  const priority = (type: string) => {
    switch (type) {
      case 'gold':
        return 3
      case 'silver':
        return 2
      case 'bronze':
        return 1
      case 'trophy':
      case 'award':
        return 4
      default:
        return 0
    }
  }

  const icons = sequence
    .split(',')
    .map(icon => icon.trim())
    .filter(Boolean)
    .sort((a, b) => {
      const diff = priority(b) - priority(a)
      if (diff !== 0) return diff
      return 0
    })

  const displayIcons = [...icons].reverse()
 
  return (
    <div className="olympic-medals">
      {displayIcons.map((iconType, index) => {
        const trimmedType = iconType.trim()
        let iconSrc = ''
        let iconAlt = ''
        
        // Handle special icon types
        if (trimmedType === 'trophy') {
          iconSrc = `/assets/achievements/trophy.png?v=${ASSET_VERSION}`
          iconAlt = 'trophy'
        } else if (trimmedType === 'award') {
          iconSrc = `/assets/achievements/award.png?v=${ASSET_VERSION}`
          iconAlt = 'award'
        } else {
          // Handle medal types
          iconSrc = `/assets/achievements/${trimmedType}-medal.png?v=${ASSET_VERSION}`
          iconAlt = `${trimmedType} medal`
        }
        
        return (
          <img 
            key={index}
            src={iconSrc} 
            alt={iconAlt} 
            className="achievement-icon" 
          />
        )
      })}
    </div>
  )
}

// Helper function to convert YouTube Shorts URL to embeddable format
const getYouTubeEmbedUrl = (url: string) => {
  // Handle YouTube Shorts URLs (youtube.com/shorts/VIDEO_ID)
  if (url.includes('youtube.com/shorts/')) {
    const videoId = url.split('youtube.com/shorts/')[1].split('?')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }
  
  // Handle regular YouTube URLs (youtube.com/watch?v=VIDEO_ID)
  if (url.includes('youtube.com/watch?v=')) {
    const videoId = url.split('v=')[1].split('&')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }
  
  // Handle youtu.be URLs (youtu.be/VIDEO_ID)
  if (url.includes('youtu.be/')) {
    const videoId = url.split('youtu.be/')[1].split('?')[0]
    return `https://www.youtube.com/embed/${videoId}`
  }
  
  return url
}

export default function CardView() {
  const { cardId } = useParams()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [claiming, setClaiming] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [card, setCard] = useState<CardResponse | null>(null)
  const [toast, setToast] = useState<{message: string, type: 'success' | 'error'} | null>(null)
  const [showClaimModal, setShowClaimModal] = useState(false)
  const [bioExpanded, setBioExpanded] = useState(false)
  const [isCardFlipped, setIsCardFlipped] = useState(false)
  const [diamondToggleOn, setDiamondToggleOn] = useState(true)

  useEffect(() => {
    let canceled = false
    async function go() {
      setLoading(true); setErr(null)
      try {
        const base = import.meta.env.VITE_API_BASE_URL || ''
        const url = new URL(`/api/cards/${cardId}`, base)
        const r = await fetch(url.toString(), { credentials: 'include' })
        if (!r.ok) throw new Error(`Card ${r.status}`)
        const j: CardResponse = await r.json()
        if (!canceled) {
          setCard(j)
        }
      } catch (e: any) {
        if (!canceled) setErr(e?.message || 'Failed to load card')
      } finally {
        if (!canceled) setLoading(false)
      }
    }
    if (cardId) go()
    return () => { canceled = true }
  }, [cardId])

  // Auto-hide toast after 3 seconds
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [toast])

  const handleOpenClaimModal = () => {
    setShowClaimModal(true)
  }

  const handleCloseClaimModal = () => {
    setShowClaimModal(false)
  }

  const handleConfirmClaim = async () => {
    if (!cardId) return
    
    setClaiming(true)
    try {
      const base = import.meta.env.VITE_API_BASE_URL || ''
      const url = new URL(`/api/cards/${cardId}/claim`, base)
      
      // Add auth token as query parameter for Safari mobile compatibility
      const authToken = localStorage.getItem('auth_token')
      if (authToken) {
        url.searchParams.set('auth_token', authToken)
        console.log('🔐 Sending auth token as query parameter for card claim:', `${authToken.substring(0, 20)}...`)
      } else {
        console.log('❌ No auth token found in localStorage for card claim')
      }
      
      console.log('🌐 Claiming card with URL:', url.toString())
      const r = await fetch(url.toString(), { 
        method: 'POST',
        credentials: 'include' 
      })
      const j = await r.json()
      
      if (!r.ok) {
        if (r.status === 401) {
          setShowClaimModal(false)
          setToast({ message: 'Please sign in to add this card to your collection', type: 'error' })
          setTimeout(() => {
            navigate('/signin?redirect=' + encodeURIComponent(`/cards/${cardId}`))
          }, 1500)
          return
        }
        throw new Error(j.message || 'Failed to claim card')
      }
      
      setShowClaimModal(false)
      setToast({ message: 'Card added to your collection!', type: 'success' })
      
      // Refresh card data to show updated status
      setCard(prev => prev ? { ...prev, owned: true, ownedByMe: true, status: 'claimed' } : null)
    } catch (e: any) {
      setShowClaimModal(false)
      setToast({ message: e?.message || 'Failed to add card to collection', type: 'error' })
    } finally {
      setClaiming(false)
    }
  }

  if (loading) {
  return (
      <div className="card-view-container">
        <div className="card-loading">Loading card…</div>
      </div>
    )
  }
  
  if (err || !card) {
    return (
      <div className="card-view-container">
        <div className="card-error">{err || 'Card not found'}</div>
        <div className="card-actions">
          <Link to="/" className="btn-secondary">Return Home</Link>
        </div>
      </div>
    )
  }

  const cardImageUrl = card.template?.image_url || card.template?.athlete?.card_image_url
  const isUnclaimed = card.status === 'unassigned' && !card.owned
  const isClaimed = card.owned
  const athlete = card.template?.athlete

  // Calculate age from DOB
  const calculateAge = (dob: string | null) => {
    if (!dob) return null
    const birthDate = new Date(dob)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const m = today.getMonth() - birthDate.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    return age
  }

  const age = calculateAge(athlete?.dob || null)

  return (
    <div className="card-page-container">
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.message}
        </div>
      )}

      <ClaimModal
        open={showClaimModal}
        onClose={handleCloseClaimModal}
        onConfirm={handleConfirmClaim}
        loading={claiming}
      />

      {/* Floating Add Button (stays visible while scrolling) */}
      {isUnclaimed && (
        <button 
          className="btn-add-floating"
          onClick={handleOpenClaimModal}
          disabled={claiming}
          aria-label="Add to collection"
        >
          <svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 6V22M6 14H22" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
          </svg>
        </button>
      )}

      <div className="card-page-content">
        {/* Header with Logo */}
        <div className="card-page-header">
          <Link to="/">
            <img src="/assets/logo-titan.svg" alt="TITAN" className="card-page-logo" />
          </Link>
          
          {card.template?.version === 'diamond' && (
            <div className={`card-diamond-toggle ${diamondToggleOn ? 'active' : ''}`} onClick={() => setDiamondToggleOn(!diamondToggleOn)}>
              <div className={`toggle-switch ${diamondToggleOn ? 'active' : ''}`}>
                <div className="toggle-knob" />
              </div>
              <div className="diamond-icon">💎</div>
            </div>
          )}
        </div>

        {/* Card Image */}
        {cardImageUrl && (
          <div 
            className={`card-page-image-wrapper ${isCardFlipped ? 'flipped' : ''}`}
            onClick={() => setIsCardFlipped(!isCardFlipped)}
          >
            <div className="card-flip-container">
              <div className="card-front">
                {card.template?.version === 'diamond' && diamondToggleOn && (
                  <div className="holographic-overlay"></div>
                )}
                <img
                  src={cardImageUrl}
                  alt={`Card #${card.serial_no} - ${athlete?.full_name}`}
                  className="card-page-image"
                />
              </div>
              {athlete?.card_back_url && (
                <div className="card-back">
                  <img
                    src={athlete.card_back_url}
                    alt={`Card back #${card.serial_no} - ${athlete?.full_name}`}
                    className="card-page-image"
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* About Section */}
        <section className="card-section">
          <h2 className="card-section-title">About</h2>
          <div className="about-grid">
            <div className="about-column">
              {athlete?.dob && (
                <div className="about-item">
                  <p className="about-value">{new Date(athlete.dob + 'T00:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
                  <p className="about-label">Date of birth</p>
                </div>
              )}
              {age && (
                <div className="about-item">
                  <p className="about-value">{age}</p>
                  <p className="about-label">Age</p>
                </div>
              )}
              {athlete?.intl_debut_year && (
                <div className="about-item">
                  <p className="about-value">{athlete.intl_debut_year}</p>
                  <p className="about-label">Career start</p>
                </div>
              )}
              {athlete?.world_ranking && (
                <div className="about-item">
                  <p className="about-value">{athlete.world_ranking}</p>
                  <p className="about-label">Current world ranking</p>
                </div>
              )}
            </div>
            <div className="about-column">
              {athlete?.hometown && (
                <div className="about-item">
                  <p className="about-value">{athlete.hometown}</p>
                  <p className="about-label">Birthplace</p>
                </div>
              )}
              {athlete?.nationality && (
                <div className="about-item">
                  <div className="nationality-row">
                    <p className="about-value">{athlete.nationality}</p>
                    {athlete.nationality === 'United States' && <span className="flag-emoji">🇺🇸</span>}
                    {athlete.nationality === 'Turkey' && <span className="flag-emoji">🇹🇷</span>}
                    {athlete.nationality === 'Great Britain' && <span className="flag-emoji">🇬🇧</span>}
                    {athlete.nationality === 'India' && <span className="flag-emoji">🇮🇳</span>}
                    {athlete.nationality === 'Colombia' && <span className="flag-emoji">🇨🇴</span>}
                    {athlete.nationality === 'Netherlands' && <span className="flag-emoji">🇳🇱</span>}
                    {athlete.nationality === 'South Korea' && <span className="flag-emoji">🇰🇷</span>}
                    {athlete.nationality === 'Denmark' && <span className="flag-emoji">🇩🇰</span>}
                  </div>
                  <p className="about-label">Nationality</p>
                </div>
              )}
              {athlete?.discipline && (
                <div className="about-item">
                  <p className="about-value">{athlete.discipline.charAt(0).toUpperCase() + athlete.discipline.slice(1)}</p>
                  <p className="about-label">Discipline</p>
                </div>
              )}
              {athlete?.best_world_ranking && (
                <div className="about-item">
                  <p className="about-value">{athlete.best_world_ranking}</p>
                  <p className="about-label">Best world ranking</p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Hero Image */}
        {athlete?.hero_image_url && (
          <div className="hero-image-wrapper">
            <img
              src={athlete.hero_image_url}
              alt={`${athlete.full_name} - Hero image`}
              className="hero-image"
            />
          </div>
        )}

        {/* Bio Section */}
        <section className="card-section">
          <h2 className="card-section-title">Bio</h2>
          <div className="bio-content">
            <p className={`bio-text ${!bioExpanded ? 'bio-truncated' : ''}`}>
              {athlete?.bio_long || athlete?.bio_short || `${athlete?.full_name} is a professional archer competing at the highest level of international competition.`}
            </p>
            {athlete?.bio_long && (
              <button 
                className="bio-read-more"
                onClick={() => setBioExpanded(!bioExpanded)}
              >
                {bioExpanded ? 'Read less' : 'Read more'}
              </button>
            )}
          </div>
        </section>

        {/* Video Section */}
        {athlete?.video_url && card.template?.version === 'diamond' && diamondToggleOn && (
          <section className="video-section">
            <div className="video-wrapper">
              {athlete.video_url.includes('drive.google.com') ? (
                <iframe
                  className="video-player"
                  src={athlete.video_url.replace('/view', '/preview')}
                  title={`${athlete?.full_name} video`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : athlete.video_url.includes('youtube.com') || athlete.video_url.includes('youtu.be') ? (
                <iframe
                  className="video-player"
                  src={getYouTubeEmbedUrl(athlete.video_url)}
                  title={`${athlete?.full_name} video`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : (
                <video 
                  className="video-player"
                  controls
                  poster={athlete?.hero_image_url || undefined}
                >
                  <source src={athlete.video_url} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              )}
            </div>
          </section>
        )}

        {/* Top Achievements */}
        <section className="card-section">
          <h2 className="card-section-title">Top achievements</h2>
          <div className="achievements-list">
            {athlete?.achievements?.length > 0 ? (
              athlete.achievements
                .sort((a, b) => a.display_order - b.display_order)
                .map((achievement, index) => (
                  <div key={index} className="achievement-item">
                    <div className="achievement-info">
                      <p className="achievement-title">{achievement.title}</p>
                      <p className="achievement-subtitle">{achievement.result}</p>
                    </div>
                    <div className="medal-group">
                      {getAchievementIcon(achievement) === 'sequence' ? (
                        // Render medal sequence from notes field
                        renderMedalSequence(achievement.notes!)
                      ) : (
                        // Render single icon
                        <img 
                          src={getAchievementIcon(achievement)} 
                          alt={`${achievement.title} icon`} 
                          className="achievement-icon single-icon" 
                        />
                      )}
                    </div>
                  </div>
                ))
            ) : (
              <p className="no-achievements">No achievements available</p>
            )}
          </div>
        </section>

        {/* Quote Section */}
        {athlete?.quote_photo_url && card.template?.version === 'diamond' && diamondToggleOn && (
          <section className="quote-section">
            <img 
              src={athlete.quote_photo_url} 
              alt={`${athlete?.full_name} quote`}
              className="quote-image"
            />
          </section>
        )}

        {/* Equipment */}
        {athlete?.equipment && athlete.equipment.length > 0 && card.template?.version === 'diamond' && diamondToggleOn && (
          <section className="card-section">
            <h2 className="card-section-title">Equipment</h2>
            <div className="equipment-grid">
              {/* Split equipment into two columns */}
              <div className="equipment-column">
                {athlete.equipment
                  .filter((_, index) => index % 2 === 0)
                  .map((eq, index) => (
                    <div key={index} className="equipment-item">
                      <p className="equipment-name">
                        {eq.brand && eq.model ? `${eq.brand} ${eq.model}` : eq.brand || eq.model || 'Unknown'}
                      </p>
                      <p className="equipment-type">{eq.category}</p>
                    </div>
                  ))}
              </div>
              <div className="equipment-column">
                {athlete.equipment
                  .filter((_, index) => index % 2 === 1)
                  .map((eq, index) => (
                    <div key={index} className="equipment-item">
                      <p className="equipment-name">
                        {eq.brand && eq.model ? `${eq.brand} ${eq.model}` : eq.brand || eq.model || 'Unknown'}
                      </p>
                      <p className="equipment-type">{eq.category}</p>
                    </div>
                  ))}
              </div>
            </div>
          </section>
        )}

        {/* Best Qualification Graph */}
        {athlete?.qualification_image_url && card.template?.version === 'diamond' && diamondToggleOn && (
          <section className="card-section">
            <h2 className="card-section-title">Best qualification</h2>
            <div className="qualification-image">
              <img
                src={athlete.qualification_image_url}
                alt={`${athlete?.full_name} qualification graph`}
                className="qualification-graph-image"
              />
            </div>
          </section>
        )}

        {/* Career Statistics */}
        {athlete?.stats && card.template?.version === 'diamond' && diamondToggleOn && (
          <section className="card-section">
            <h2 className="card-section-title">Career statistics</h2>
            <div className="stats-list">
              {/* Win Percentage */}
              {athlete.stats.win_percentage && (
                <div className="stat-item">
                  <div className="stat-content">
                    <div className="stat-icon">
                      <img 
                        src="/assets/career-statistics/win-percentage.png" 
                        alt="Win percentage icon"
                        width="24"
                        height="24"
                      />
                    </div>
                    <div className="stat-info">
                      <p className="stat-name">Win percentage</p>
                      <p className="stat-description">{athlete.stats.extras?.wins || 0}-{athlete.stats.extras?.losses || 0}</p>
                    </div>
                  </div>
                  <p className="stat-value">{athlete.stats.win_percentage}%</p>
                </div>
              )}

              {/* Average Arrow */}
              {athlete.stats.average_arrow && (
                <div className="stat-item">
                  <div className="stat-content">
                    <div className="stat-icon">
                      <img 
                        src="/assets/career-statistics/average-arrow.png" 
                        alt="Average arrow icon"
                        width="24"
                        height="24"
                      />
                    </div>
                    <div className="stat-info">
                      <p className="stat-name">Average arrow</p>
                      <p className="stat-description">Out of 10</p>
                    </div>
                  </div>
                  <p className="stat-value">{athlete.stats.average_arrow}</p>
                </div>
              )}

              {/* Tiebreak Win Rate */}
              {athlete.stats.tiebreak_win_rate && (
                <div className="stat-item">
                  <div className="stat-content">
                    <div className="stat-icon">
                      <img 
                        src="/assets/career-statistics/tie-breaks.png" 
                        alt="Tiebreaks icon"
                        width="24"
                        height="24"
                      />
                    </div>
                    <div className="stat-info">
                      <p className="stat-name">Tiebreaks</p>
                      <p className="stat-description">{athlete.stats.extras?.tiebreak_wins || 0}-{athlete.stats.extras?.tiebreak_losses || 0}</p>
                    </div>
                  </div>
                  <p className="stat-value">{athlete.stats.tiebreak_win_rate}%</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Action Photo */}
        {athlete?.action_photo_url && (
          <section className="action-photo-section">
            <img 
              src={athlete.action_photo_url} 
              alt={`${athlete?.full_name} in action`}
              className="action-photo"
            />
          </section>
        )}

        {/* Socials */}
        {athlete?.socials && Object.keys(athlete.socials).length > 0 && (
          <section className="card-section">
            <h2 className="card-section-title">Socials</h2>
            <div className="socials-row">
              {athlete.socials.instagram && (
                <a 
                  href={athlete.socials.instagram} 
                  className="social-icon" 
                  aria-label="Instagram"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img 
                    src="/assets/socials-icons/instagram.png" 
                    alt="Instagram"
                    width="33"
                    height="33"
                  />
                </a>
              )}
              {athlete.socials.facebook && (
                <a 
                  href={athlete.socials.facebook} 
                  className="social-icon" 
                  aria-label="Facebook"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <img 
                    src="/assets/socials-icons/facebook.png" 
                    alt="Facebook"
                    width="33"
                    height="33"
                  />
                </a>
              )}
            </div>
          </section>
        )}

        {/* Sponsors */}
        {athlete?.sponsors && athlete.sponsors.length > 0 && (
          <section className="card-section">
            <h2 className="card-section-title">Sponsors</h2>
            <div className="sponsors-grid">
              {athlete.sponsors.map((sponsor, index) => {
                // Safari mobile compatible rendering - avoid ternary operator
                if (sponsor.url) {
                  return (
                    <a 
                      key={index} 
                      href={sponsor.url} 
                      className="sponsor-logo"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <img 
                        src={sponsor.logo_url} 
                        alt={sponsor.name}
                      />
                    </a>
                  )
                } else {
                  return (
                    <div key={index} className="sponsor-logo">
                      <img 
                        src={sponsor.logo_url} 
                        alt={sponsor.name}
                      />
                    </div>
                  )
                }
              })}
            </div>
          </section>
        )}

        {/* Footer */}
        <div className="card-page-footer">
          <p className="footer-disclaimer">
            All card statistics, records, and other details reflect data available as of August 9, 2025.
          </p>
          <img src="/assets/logo-titan.svg" alt="TITAN" className="footer-logo" />
        </div>
      </div>
    </div>
  )
}