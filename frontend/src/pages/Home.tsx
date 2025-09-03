// src/pages/Home.tsx
import { Link } from 'react-router-dom'
import { Reveal, ParallaxY } from '../components/Reveal'
import './home.css'

export default function Home(){
  return (
    <div className="home">
       <div className="top-bg">
        {/* HERO */}
        <section id="hero" className="hero">
          <div className="container hero__grid">
            <Reveal>
              <div className="hero__copy">
                <h1 className="hero__title">SERIES ONE: A NEW ERA.</h1>
                <p className="hero__body">
                  Tap your card to reveal exclusive athlete stories, stats, and gear insights — powered by NFC.
                  Collect all 8 cards featuring the sport’s top athletes to unlock the bonus 9th.
                </p>
                <div className="hero__cta">
                  <Link to="/buy" className="btn-primary">Buy Now</Link>
                  <Link to="/#about" className="btn-ghost">Learn More</Link>
                </div>
                <div className="hero__license">
                  <img src="/assets/world-archery.png" alt="World Archery" />
                  <div className="license__caption">Officially Licensed Collectibles</div>
                </div>
              </div>
            </Reveal>

            <ParallaxY move={[0, -30]}>
              <div className="hero__art">
                <div className="pack-wrap">
                  <img src="/assets/pack-placeholder.png" alt="Series One Pack" />
                </div>
              </div>
            </ParallaxY>
          </div>
        </section>

        {/* PHYSICAL MEETS DIGITAL (video first, text below) */}
        <section id="physical" className="physical">
          <div className="physical__video">
            <video
              className="bgvid"
              autoPlay
              muted
              loop
              playsInline
              poster="/assets/pack-placeholder.png"
            >
              <source src="/assets/phone-video.webm" type="video/webm" />
              <source src="/assets/phone-video.mp4" type="video/mp4" />
            </video>
            <div className="video__overlay" />
          </div>

          {/* text below the video */}
          <div className="container physical__copy">
            <h3><span className="accent">Physical</span> meets digital</h3>
            <p className="physical__para">
            Each card is embedded with NFC technology — just tap 
              <br className="br-desktop" />
              your phone to unlock exclusive content, see personal stats,
              <br className="br-desktop" />
              training insights & gear breakdowns.
            </p>
          </div>

        </section>

       </div>
      

      {/* VALUE POINTS */}
      <section className="value">
        <div className="container value__grid">
          <Reveal delay={0.05}>
            <div className="value__card">
              <h3>Direct support to the athletes</h3>
              <p>Every pack purchased directly contributes to featured athletes.</p>
            </div>
          </Reveal>
          <Reveal delay={0.15}>
            <div className="value__card">
              <h3>Verified authenticity</h3>
              <p>NFC tags are verified on tap and bound to a single collection.</p>
            </div>
          </Reveal>
          <Reveal delay={0.25}>
            <div className="value__card">
              <h3>Unlock the bonus card</h3>
              <p>Collect all 8 to unlock an exclusive 9th bonus card.</p>
            </div>
          </Reveal>
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
                  Still not working? Contact us at <a href="mailto:support@titansports.ca">support@titansports.ca</a>,
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
            <form className="contact__form" onSubmit={(e)=>{e.preventDefault(); alert('Thanks! We will get back to you.')}}>
              <div className="row">
                <label>First name<input required/></label>
                <label>Last name<input required/></label>
              </div>
              <label>Email<input type="email" required/></label>
              <label>Message<textarea rows={5} required/></label>
              <button className="btn-primary" type="submit">Send</button>
            </form>
          </Reveal>
        </div>
      </section>
    </div>
  )
}
