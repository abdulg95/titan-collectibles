import { sf } from "./shopify";

const CART_FRAGMENT = `
fragment CartFragment on Cart {
  id
  totalQuantity
  cost { subtotalAmount { amount currencyCode } totalAmount { amount currencyCode } }
  lines(first:50){edges{node{id quantity merchandise{... on ProductVariant{id title product{title} price{amount currencyCode}}}}}
  checkoutUrl
}`;

const CART_CREATE = `
mutation CartCreate($lines:[CartLineInput!], $buyerIdentity:CartBuyerIdentityInput, $attributes:[AttributeInput!]){
  cartCreate(input:{lines:$lines, buyerIdentity:$buyerIdentity, attributes:$attributes}){
    cart{...CartFragment}
    userErrors{field message}
  }
}
${CART_FRAGMENT}`;

const CART_LINES_ADD = `
mutation CartLinesAdd($cartId:ID!, $lines:[CartLineInput!]!){
  cartLinesAdd(cartId:$cartId, lines:$lines){
    cart{...CartFragment}
    userErrors{field message}
  }
}
${CART_FRAGMENT}`;

const CART_QUERY = `
query Cart($id:ID!){ cart(id:$id){...CartFragment} }
${CART_FRAGMENT}`;

export async function getCart(){
  const id = localStorage.getItem("cartId");
  if(!id) return null;
  try { return (await sf(CART_QUERY, { id })).cart; } catch { localStorage.removeItem("cartId"); return null; }
}

export async function addToCart(variantId:string, qty=1, opts?:{ buyerEmail?:string; appUserId?:string }){
  const existing = await getCart();
  const attributes = opts?.appUserId ? [{ key:"app_user_id", value: opts.appUserId }] : undefined;
  if(!existing){
    const data:any = await sf(CART_CREATE, {
      lines:[{ merchandiseId: variantId, quantity: qty }],
      buyerIdentity: opts?.buyerEmail ? { email: opts.buyerEmail } : undefined,
      attributes
    });
    const cart = data.cartCreate.cart;
    localStorage.setItem("cartId", cart.id);
    return cart;
  } else {
    const data:any = await sf(CART_LINES_ADD, { cartId: existing.id, lines:[{ merchandiseId: variantId, quantity: qty }] });
    return data.cartLinesAdd.cart;
  }
}
