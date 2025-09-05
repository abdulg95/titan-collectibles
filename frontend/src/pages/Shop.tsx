import { useEffect, useState } from 'react'
import ProductCard from '../components/ProductCard'
import ProductDescription from '../components/ProductDescription'
import './shop.css'

type User = { id: string; email: string; name?: string | null } | null

const STORE_DOMAIN = import.meta.env.VITE_SHOPIFY_STORE_DOMAIN
const STOREFRONT_TOKEN = import.meta.env.VITE_STOREFRONT_API_TOKEN
const STOREFRONT_API_VERSION = import.meta.env.VITE_STOREFRONT_API_VERSION || '2025-01'
const VARIANT_ID = import.meta.env.VITE_SHOPIFY_VARIANT_ID // e.g. gid://shopify/ProductVariant/1234567890
const API = import.meta.env.VITE_API_BASE_URL || ''

export default function Shop(){
  const [user, setUser] = useState<User>(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const shopReady = !!(STORE_DOMAIN && STOREFRONT_TOKEN && VARIANT_ID)

  useEffect(()=>{ (async()=>{
    try{
      const r = await fetch(`${API}/api/auth/me`, { credentials:'include' })
      const j = await r.json()
      setUser(j.user || null)
    }catch(_e){ /* ignore */ }
    setLoading(false)
  })()},[])

  async function createCheckout(){
    if(!shopReady){
      alert('Shopify is not configured yet.')
      return
    }
    setBusy(true)
    try{
      const res = await fetch(`https://${STORE_DOMAIN}/api/${STOREFRONT_API_VERSION}/graphql.json`,{
        method:'POST',
        headers:{
          'Content-Type':'application/json',
          'X-Shopify-Storefront-Access-Token': STOREFRONT_TOKEN as string,
        },
        body: JSON.stringify({
          query: `
            mutation($lineItems:[CheckoutLineItemInput!]!){
              checkoutCreate(input:{ lineItems:$lineItems }) {
                checkout { webUrl }
                userErrors { field message }
              }
            }`,
          variables: { lineItems: [{ variantId: VARIANT_ID, quantity: 1 }] }
        })
      })
      const j = await res.json()
      const url = j?.data?.checkoutCreate?.checkout?.webUrl
      if(url){
        window.location.href = url
      }else{
        console.error(j)
        alert('Could not start checkout.')
      }
    }finally{
      setBusy(false)
    }
  }

  function handleBuy(){
    if(loading) return
    if(!user){
      // Open your auth modal if you wired a window event; fall back to simple redirect
      window.dispatchEvent(new CustomEvent('open-auth-modal'))
      // fallback:
      // window.location.href = '/?auth=1'
      return
    }
    createCheckout()
  }

  return (
    <div className="shop-page">
      <div className="container">

        <ProductCard
          title="Series One – Standard Pack"
          series="Titan Collectibles"
          onBuy={()=>{/* TODO: hook to Shopify checkout */}}
          packImg="/assets/pack-placeholder.png"
          leftCardImg="/assets/card-left.png"
          rightCardImg="/assets/card-right.png"
        >
          <p>8 cards per pack. Chance to unlock the bonus 9th card.</p>
        </ProductCard>
        <ProductDescription />

        {/* Add another product card the same way */}
      </div>
    </div>
  )
}
