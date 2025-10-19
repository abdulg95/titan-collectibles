// src/pages/Product.tsx
import { useParams } from "react-router-dom"
import "../pages/shop.css"
import AddToCartButton from '../components/AddToCartButton';

export default function ProductDescription(){

  // Temporary data; replace with Shopify data later
  const product = {
    series: "Series One",
    title: "World Archery",
    price: "$20",
    bullets: [
      "4 cards per pack",
      "Guaranteed 1 diamond card per pack",
      "Digital cards include:",
      "Athlete sports card",
      "About",
      "Bio",
      "Exclusive video*",
      "Top achievements",
      "Quote*",
      "Equipment*",
      "Best qualification*",
      "Career statistics*",
      "Socials",
      "Sponsors",
      "*Only available on diamond tier cards"
    ],
    details: [
      "Step into the world of elite archery with the first-ever officially licensed World Archery trading card series. Each pack features athletes at the top of their game—Olympians, world champions, and stars who define the sport.",
      "Every card is embedded with NFC technology, unlocking exclusive digital content including athlete stories, in-depth stats, and rare equipment insights—just tap with your phone to explore the gear and grit behind the performance.",
      "Collect all 8 cards in the Series One set to reveal a secret 9th card—a rare, unlockable card that would be essential for any archery fan’s collection.",
      "Whether you're a fan, a collector, or new to the sport, this is more than just a pack of cards—it's a portal into precision, power, and passion."
    ],
    specs: [
      ["Card dimensions", "63.5mm x 88.9mm"],
      ["Type", "Foil pack"]
    ]
  }

  return (
    <div className="container product-detail">
      {/* --- your existing hero/media goes above this --- */}

      {/* Meta row (series, name, price + CTA) */}
      <div className="pd__meta">
        <div className="pd__meta-left">
          <div className="pd__series">{product.series}</div>
          <div className="pd__name">{product.title}</div>
          <div className="pd__price">{product.price}</div>
        </div>
        {/* <button
          className="pill-btn"
          onClick={()=>alert("Hook this up to Shopify add-to-cart")}
        >
          Add to Cart
        </button> */}
        <AddToCartButton handle="series-1-card-pack" style="primary" />
      </div>

      {/* === The info card === */}
      <article className="pd__card">
        {/* Description */}
        <section className="pd__section">
          <h3 className="pd__h">Description</h3>
          <ul className="pd__bullets">
            {product.bullets.map((b,i)=><li key={i}>{b}</li>)}
          </ul>
        </section>

        {/* Details */}
        <section className="pd__section">
          <h3 className="pd__h">Details</h3>
          {product.details.map((p,i)=><p key={i}>{p}</p>)}
        </section>

        {/* Specs */}
        <section className="pd__section">
          <h3 className="pd__h">Specs</h3>
          <dl className="pd__specs">
            {product.specs.map(([k,v])=>(
              <div className="pd__spec-row" key={k}>
                <dt>{k}</dt><dd>{v}</dd>
              </div>
            ))}
          </dl>
        </section>
      </article>
    </div>
  )
}
