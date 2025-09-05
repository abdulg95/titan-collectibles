// src/lib/shopify.ts
const DOMAIN = import.meta.env.VITE_SHOPIFY_STORE_DOMAIN!;
const TOKEN = import.meta.env.VITE_STOREFRONT_API_TOKEN!;
const API = import.meta.env.VITE_STOREFRONT_API_VERSION || '2025-01';
const ENDPOINT = `https://${DOMAIN}/api/${API}/graphql.json`;

export async function sf<T>(query: string, variables?: Record<string, any>): Promise<T> {
  const r = await fetch(ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': TOKEN,
    },
    body: JSON.stringify({ query, variables }),
  });

  // network / HTTP errors
  if (!r.ok) {
    const txt = await r.text().catch(() => '');
    throw new Error(`Shopify ${r.status}: ${txt || r.statusText}`);
  }

  const j = await r.json();
  if (j.errors?.length) {
    // surface GraphQL errors nicely
    const msg = j.errors.map((e: any) => e.message).join('; ');
    throw new Error(msg);
  }
  return j.data;
}

// --- Product (by handle) ---
export async function getProductByHandle(handle: string) {
  const q = `
    query Product($handle: String!) {
      product(handle: $handle) {
        id
        title
        descriptionHtml
        handle
        variants(first: 10) {
          nodes {
            id
            title
            availableForSale
            price { amount currencyCode }  # MoneyV2
          }
        }
        images(first: 10) { nodes { url altText } }
      }
    }`;
  const data = await sf<{product:any}>(q, { handle });
  return data.product;
}

// Optional helper: first variant id for quick “Add to Cart”
export async function getFirstVariantIdByHandle(handle: string): Promise<string> {
  const q = `
    query V($handle: String!) {
      product(handle: $handle) {
        variants(first: 1) { nodes { id availableForSale } }
      }
    }`;
  const data = await sf<{product:{variants:{nodes:{id:string,availableForSale:boolean}[]}}}>(q, { handle });
  const v = data.product?.variants?.nodes?.[0];
  if (!v?.id) throw new Error(`No variant found for ${handle}`);
  if (!v.availableForSale) throw new Error(`Variant for ${handle} is not available`);
  return v.id;
}

// --- Cart helpers ---
const CART_ID_KEY = 'cartId';
const CHECKOUT_URL_KEY = 'checkoutUrl';

function getCartId(){ try { return localStorage.getItem(CART_ID_KEY); } catch { return null; } }
function setCartId(id:string){ try { localStorage.setItem(CART_ID_KEY, id); } catch {} }
function setCheckoutUrl(u:string){ try { localStorage.setItem(CHECKOUT_URL_KEY, u); } catch {} }
function getStoredCheckoutUrl(){ try { return localStorage.getItem(CHECKOUT_URL_KEY) || ''; } catch { return ''; } }

export async function ensureCart(): Promise<{id:string, checkoutUrl:string, totalQuantity:number}> {
  const exist = getCartId();
  if (exist) {
    // fetch fresh so we have current checkoutUrl/quantity
    const d = await sf<{cart:{id:string, checkoutUrl:string, totalQuantity:number}}>(`
      query GetCart($id: ID!) { cart(id: $id) { id checkoutUrl totalQuantity } }
    `, { id: exist });
    if (d.cart?.id) {
      setCheckoutUrl(d.cart.checkoutUrl);
      return d.cart;
    }
  }

  const d = await sf<{cartCreate:{cart:{id:string, checkoutUrl:string, totalQuantity:number}, userErrors:any[]}}>(`
    mutation CreateCart {
      cartCreate(input: {}) {
        cart { id checkoutUrl totalQuantity }
        userErrors { field message }
      }
    }
  `);
  const { cart, userErrors } = d.cartCreate;
  if (!cart) throw new Error((userErrors||[]).map((e:any)=>e.message).join('; ') || 'Failed to create cart');

  setCartId(cart.id);
  setCheckoutUrl(cart.checkoutUrl);
  return cart;
}

export async function addToCart(variantId: string, quantity = 1){
  const cart = await ensureCart();
  const d = await sf<{cartLinesAdd:{
    cart:{ id:string, checkoutUrl:string, totalQuantity:number },
    userErrors:{field:string[], message:string}[]
  }}>(`
    mutation AddLines($cartId: ID!, $lines: [CartLineInput!]!) {
      cartLinesAdd(cartId: $cartId, lines: $lines) {
        cart { id checkoutUrl totalQuantity }
        userErrors { field message }
      }
    }`,
    { cartId: cart.id, lines: [{ quantity, merchandiseId: variantId }] }
  );

  const { cart: updated, userErrors } = d.cartLinesAdd;
  if (userErrors?.length) throw new Error(userErrors.map(e=>e.message).join('; '));
  if (updated?.checkoutUrl) setCheckoutUrl(updated.checkoutUrl);
  return updated; // includes totalQuantity for your UI
}

export async function getCheckoutUrl(): Promise<string> {
  const id = getCartId();
  if (!id) return getStoredCheckoutUrl() || '';
  const d = await sf<{cart:{checkoutUrl:string} }>(`
    query GetCart($id: ID!) { cart(id: $id) { checkoutUrl } }
  `, { id });
  const url = d.cart?.checkoutUrl || getStoredCheckoutUrl();
  if (url) setCheckoutUrl(url);
  return url;
}

export async function goToCheckout() {
  const url = await getCheckoutUrl();
  if (url) window.location.href = url;
}

// --- Cart (full) ---
export type Money = { amount: string; currencyCode: string };
export type CartLine = {
  id: string;
  quantity: number;
  merchandise: {
    id: string;                // variant id
    title: string;
    product: { title: string; handle: string; images: { nodes: { url: string }[] } };
    image?: { url: string; altText: string | null };
    price: Money;
  };
};

export type CartData = {
  id: string;
  checkoutUrl: string;
  totalQuantity: number;
  cost: { subtotalAmount: Money; totalAmount: Money };
  lines: { nodes: CartLine[] };
};

export async function getCart(id: string): Promise<CartData | null> {
  const q = `
    query GetCart($id: ID!) {
      cart(id: $id) {
        id
        checkoutUrl
        totalQuantity
        cost {
          subtotalAmount { amount currencyCode }
          totalAmount { amount currencyCode }
        }
        lines(first: 50) {
          nodes {
            id
            quantity
            merchandise {
              ... on ProductVariant {
                id
                title
                price { amount currencyCode }
                product {
                  title handle
                  images(first:1){ nodes { url } }
                }
              }
            }
          }
        }
      }
    }`;
  const d = await sf<{ cart: CartData | null }>(q, { id });
  return d.cart;
}

export async function updateLineQuantity(cartId: string, lineId: string, quantity: number) {
  const q = `
    mutation UpdateLine($cartId: ID!, $lines: [CartLineUpdateInput!]!) {
      cartLinesUpdate(cartId: $cartId, lines: $lines) {
        cart { id checkoutUrl totalQuantity }
        userErrors { field message }
      }
    }`;
  const vars = { cartId, lines: [{ id: lineId, quantity }] };
  const d = await sf<{ cartLinesUpdate: { cart: { id: string, checkoutUrl: string, totalQuantity: number } | null, userErrors: any[] } }>(q, vars);
  const { userErrors } = d.cartLinesUpdate;
  if (userErrors?.length) throw new Error(userErrors.map((e:any)=>e.message).join('; '));
  return d.cartLinesUpdate.cart;
}

export async function removeLine(cartId: string, lineId: string) {
  const q = `
    mutation RemoveLine($cartId: ID!, $lineIds: [ID!]!) {
      cartLinesRemove(cartId: $cartId, lineIds: $lineIds) {
        cart { id checkoutUrl totalQuantity }
        userErrors { field message }
      }
    }`;
  const vars = { cartId, lineIds: [lineId] };
  const d = await sf<{ cartLinesRemove: { cart: { id: string, checkoutUrl: string, totalQuantity: number } | null, userErrors: any[] } }>(q, vars);
  const { userErrors } = d.cartLinesRemove;
  if (userErrors?.length) throw new Error(userErrors.map((e:any)=>e.message).join('; '));
  return d.cartLinesRemove.cart;
}

