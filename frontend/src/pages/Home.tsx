// src/pages/Home.tsx
import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { Reveal, ParallaxY } from '../components/Reveal'
import './home.css'

export default function Home(){
  const [currentTextIndex, setCurrentTextIndex] = useState(0)
  const phoneScreenRef = useRef<HTMLDivElement>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitMessage, setSubmitMessage] = useState<string | null>(null)

  const scrollTexts = [
    {
      title: "Unlock the",
      highlight: "digital",
      subtitle: "experience",
      description: "NFC-powered instant access to athlete digital cards. It’s your direct link to athletes you love."
    },
    {
      title: "Unlock the",
      highlight: "digital",
      subtitle: "experience",
      description: ""
    },
    {
      title: "Exclusive",
      highlight: "content",
      subtitle: ""
    },
    {
      title: "Exclusive",
      highlight: "content",
      subtitle: ""
    },
    {
      title: "",
      highlight: "",
      subtitle: "",
      description: ""
    }
  ]

  useEffect(() => {
    const handleScroll = () => {
      if (!phoneScreenRef.current) return
      
      const scrollTop = phoneScreenRef.current.scrollTop
      const scrollHeight = phoneScreenRef.current.scrollHeight - phoneScreenRef.current.clientHeight
      const scrollPercentage = scrollTop / scrollHeight
      
      // Adjust thresholds to make last section trigger lower
      // Sections: 0-20%, 20-40%, 40-60%, 60-85%, 85-100%
      let sectionIndex = 0
      if (scrollPercentage >= 0.20) sectionIndex = 1
      if (scrollPercentage >= 0.40) sectionIndex = 2
      if (scrollPercentage >= 0.60) sectionIndex = 3
      if (scrollPercentage >= 0.85) sectionIndex = 4
      
      setCurrentTextIndex(sectionIndex)
    }

    const phoneScreen = phoneScreenRef.current
    if (phoneScreen) {
      phoneScreen.addEventListener('scroll', handleScroll)
      return () => phoneScreen.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const handleContactSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsSubmitting(true)
    setSubmitMessage(null)

    const form = e.currentTarget
    const formData = new FormData(form)
    
    const data = {
      firstName: formData.get('firstName') as string,
      lastName: formData.get('lastName') as string,
      email: formData.get('email') as string,
      message: formData.get('message') as string,
    }

    try {
      const API = import.meta.env.VITE_API_BASE_URL || ''
      const url = new URL('/api/contact', API).toString()
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const result = await response.json()

      if (response.ok) {
        setSubmitMessage(result.message || 'Thanks! We will get back to you.')
        form.reset()
      } else {
        setSubmitMessage(result.error || 'Something went wrong. Please try again.')
      }
    } catch (error) {
      setSubmitMessage('Failed to send message. Please try again later.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={`home ${currentTextIndex === 4 ? 'dark-background' : ''}`}>
       <div className="top-bg">
        {/* HERO */}
        <section id="hero" className="hero">
          <div className="container hero__grid">
            {/* Mobile: Image first, Desktop: Text first */}
            <div className="hero__art-mobile-first">
              <div className="hero__art">
                <div className="pack-wrap">
                  <img src="/assets/pack-placeholder.png" alt="Series One Pack" />
                </div>
              </div>
            </div>

            <Reveal className="hero__copy-mobile-second">
              <div className="hero__copy">
                <h1 className="hero__title">SERIES ONE: A NEW ERA.</h1>
                <p className="hero__body">
                  Tap your card to reveal exclusive athlete stories, stats, and gear insights — powered by NFC.
                  Collect all 8 cards featuring the sport's top athletes to unlock the bonus 9th.
                </p>
                <div className="hero__cta">
                  <Link to="/buy" className="btn-primary">Buy Now</Link>
                  <a 
                    href="#"
                    className="btn-ghost"
                    onClick={(e) => {
                      e.preventDefault()
                      const aboutEl = document.getElementById('about')
                      if (aboutEl) {
                        aboutEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      }
                    }}
                  >
                    Learn More
                  </a>
                </div>
                <div className="hero__license">
                  <img src="/assets/world-archery.png" alt="World Archery" />
                  <div className="license__caption">Officially Licensed Collectibles</div>
                </div>
              </div>
            </Reveal>
          </div>
        </section>

            {/* PHYSICAL MEETS DIGITAL (video first, text below) */}
            <section id="physical" className="physical">
              <div className="container physical__grid">
                <div className="physical__image">
                  <div className="phone-wrap">
                    {/* Scrollable screen area */}
                    <div className="phone-screen" ref={phoneScreenRef}>
                      {/* The Ella features image is taller than the screen so you can scroll */}
                      <img 
                        src="/assets/card-features/Ella features call out prototype.png" 
                        alt="Ella features" 
                        className="screen-photo"
                      />
                    </div>

                    {/* The iPhone frame sits on top; pointer-events none so scroll still works */}
                    <img 
                      src="/assets/card-features/iPhone 14 Pro.png" 
                      alt="iPhone frame" 
                      className="phone-frame"
                    />
                  </div>
                </div>
                <div className="physical__content">
                  <h3 className="physical__title">
                    <span className="accent">{scrollTexts[currentTextIndex].title} </span>
                    <span className="highlight">{scrollTexts[currentTextIndex].highlight}</span>
                    <br />
                    <span className="highlight">{scrollTexts[currentTextIndex].subtitle}</span>
                  </h3>
                  {scrollTexts[currentTextIndex].description && (
                    <p className="physical__para">
                      {scrollTexts[currentTextIndex].description}
                    </p>
                  )}
                  {currentTextIndex === 1 && (
                    <div className="bio-pill">
                      BIO
                    </div>
                  )}
                  {currentTextIndex === 2 && (
                    <div className="pills-container">
                      <div className="personal-video-pill">
                        Personal Video
                      </div>
                      <div className="diamond-feature-pill">
                        <span className="pill-icon">💎</span>
                        Diamond Feature
                      </div>
                    </div>
                  )}
                  {currentTextIndex === 3 && (
                    <div className="pills-container">
                      <div className="personal-video-pill">
                        Mental Game
                      </div>
                      <div className="diamond-feature-pill">
                        <span className="pill-icon">💎</span>
                        Diamond Feature
                      </div>
                    </div>
                  )}
                  {currentTextIndex === 4 && (
                    <div className="titan-icon-container">
                      <img src="/assets/titan-icon 1.png" alt="TITAN" className="titan-icon" />
                    </div>
                  )}
                </div>
              </div>
            </section>

       </div>
      

      {/* ABOUT SECTION */}
      <section className="about-section">
        <div className="container about-section__content">
          <div className="about-section__amount">
            $<span className="amount-spacing">1800+</span>
          </div>
          <div className="about-section__text">
            <h3 className="about-section__title">
              Direct support
              <span className="about-section__accent"> to<br />the athletes</span>
            </h3>
            <p className="about-section__description">
              Every pack sold puts money straight into the hands of the athletes featured, helping fund their training and competitions. When you collect Titan cards, you're supporting the athletes you love.
            </p>
          </div>
        </div>
      </section>

      {/* UNLOCK BONUS CARD SECTION */}
      <section className="unlock-bonus-section">
        <div className="container unlock-bonus-section__content">
          <div className="unlock-bonus-section__image">
            <img 
              src="/assets/Diamond-card-package.png" 
              alt="Bonus Card" 
              className="bonus-card-image"
            />
          </div>
          <div className="unlock-bonus-section__text">
            <h3 className="unlock-bonus-section__title">
              Unlock<span className="unlock-bonus-section__accent"> the </span>
              <span className="unlock-bonus-section__highlight">bonus card</span>
            </h3>
            <p className="unlock-bonus-section__description">
              Collect all 8 cards in the Series One set to unlock the exclusive 9th card. Trust us, it's a card most archery fans would want.
            </p>
          </div>
        </div>
      </section>

      {/* VIDEO SECTION */}
      <section className="video-section">
        <div className="video-section__container">
          <iframe 
            className="video-section__iframe"
            src="https://www.youtube.com/embed/j_bccP1N0JA?autoplay=1&mute=1&loop=1&playlist=j_bccP1N0JA"
            title="TITAN Website Video"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      </section>

      {/* ABOUT */}
      <section id="about" className="about">
        <div className="container about__grid">
          <div className="about__copy">
            <h2>About Titan</h2>
            <p>
              Titan began with <strong>Vanessa</strong>, <strong>Matt</strong>, and <strong>Brody</strong>—three creatives who
              wanted to see athletes in more sports featured on the front of sports cards, starting with the one Vanessa had a
              lifelong connection to: <strong>archery</strong>. Matt&apos;s expertise in manufacturing and NFC tech made the
              product possible, while Brody&apos;s creative brilliance shaped the brand and design.
            </p>
            <p>
              Shortly after, the team brought on <strong>Michael</strong> and <strong>Abdul</strong> to oversee the vision,
              guide it forward through sharp project management, and with Abdul&apos;s technical skills, we turned an ambitious
              idea into something real. Together, we&apos;re building a platform that honors the athletes pushing their sports
              forward.
            </p>
          </div>

          <div className="about__image">
            <img src="/assets/about-team.jpg" alt="Titan team" />
          </div>
        </div>
      </section>

      {/* CELEBRATE THE SPORT SECTION */}
      <section className="celebrate-section">
        <div className="celebrate-section__background">
          <img src="/GWANGJU_TITAN_11SEP25_0022.jpg" alt="Celebrate the sport" />
        </div>
        <div className="container celebrate-section__content">
          <div className="celebrate-section__text">
            <h2 className="celebrate-section__title">
              celebrate the sport.<br />
              honour the athlete.
            </h2>
            <Link to="/buy" className="btn-primary celebrate-section__button">
              Buy Now
            </Link>
          </div>
        </div>
      </section>

      {/* FAQS */}
      <section id="faqs" className="faqs">
        <div className="container">
          <Reveal><h2>FAQs</h2></Reveal>
          <Reveal delay={0.05}>
            <p className="faq__intro">
              Find answers to common questions about our sports cards and the purchasing process.
            </p>
          </Reveal>

          <div className="faq__list">
            <Reveal delay={0.10}>
              <details>
                <summary>What are Titan cards?</summary>
                <p>
                  Titan cards are the first officially licensed sports cards featuring the world’s top athletes.
                  Each card includes NFC technology, unlocking exclusive digital content. Plus, every purchase
                  supports the athletes directly.
                </p>
              </details>
            </Reveal>

            <Reveal delay={0.15}>
              <details>
                <summary>How do I buy?</summary>
                <p>
                  Purchasing Titan cards is simple! Just browse our collection, select your desired pack, and
                  proceed to checkout. You can create an account for a smoother experience.
                </p>
              </details>
            </Reveal>

            <Reveal delay={0.20}>
              <details>
                <summary>What’s the secret card?</summary>
                <p>
                  For the first ever pack, you can collect all 8 cards to unlock a special 9th card. This
                  exclusive card features unique content and features an athlete you’d definitely want to collect.
                </p>
              </details>
            </Reveal>

            <Reveal delay={0.25}>
              <details>
                <summary>Can I return cards?</summary>
                <p>
                  We want you to be satisfied with your purchase. If you encounter any issues, please contact our
                  support team. Returns are accepted under specific conditions.
                </p>
              </details>
            </Reveal>

            <Reveal delay={0.30}>
              <details>
                <summary>Are the cards collectible?</summary>
                <p>
                  Absolutely! Titan cards are designed for collectors and fans alike. With limited editions and
                  exclusive content, they hold great value. Start your collection today!
                </p>
              </details>
            </Reveal>

            <Reveal delay={0.35}>
              <details>
                <summary>How do I get the NFC to work?</summary>
                <p>To activate the NFC feature on your Titan card:</p>
                <ol>
                  <li>
                    Unlock your phone and make sure NFC is turned on (usually found in your device’s settings under
                    “Connections” or “Wireless &amp; Networks”).
                  </li>
                  <li>
                    Hold the back of your phone close to the NFC logo on the Titan card — usually near the top or
                    center of your device.
                  </li>
                  <li>Tap and wait a second — a link should automatically pop up on your screen.</li>
                </ol>
                <p>If nothing happens:</p>
                <ul>
                  <li>Make sure your phone supports NFC.</li>
                  <li>Try removing your phone case if it’s thick or metal.</li>
                  <li>Move your phone slowly around the card in case the reader is in a different spot.</li>
                </ul>
                <p>
                  Still not working? Contact us at <a href="mailto:support@titansportshq.com">support@titansportshq.com</a>,
                  and we’ll help you out.
                </p>
              </details>
            </Reveal>

            <Reveal delay={0.40}>
              <details>
                <summary>Can I only collect digital cards?</summary>
                <p>
                  Nope — Titan cards are both physical and digital. Every card comes as a premium printed collectible
                  with an embedded NFC chip that links to its digital twin. So you get the best of both worlds:
                  something to hold and display, plus a digital version to trade, showcase, or verify authenticity online.
                </p>
              </details>
            </Reveal>
          </div>
        </div>
      </section>


      {/* CONTACT */}
      <section id="contact" className="contact">
        <div className="container contact__grid">
          <Reveal><h2>Still have questions?</h2></Reveal>
          <Reveal delay={0.08}>
            <form className="contact__form" onSubmit={handleContactSubmit}>
              <div className="row">
                <label>First name<input name="firstName" required/></label>
                <label>Last name<input name="lastName" required/></label>
              </div>
              <label>Email<input name="email" type="email" required/></label>
              <label>Message<textarea name="message" rows={5} required/></label>
              {submitMessage && (
                <div className={submitMessage.includes('Thank') ? 'contact__success' : 'contact__error'}>
                  {submitMessage}
                </div>
              )}
              <button className="btn-secondary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Sending...' : 'Contact Us'}
              </button>
            </form>
          </Reveal>
        </div>
      </section>
    </div>
  )
}
