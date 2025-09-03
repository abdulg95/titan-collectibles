export async function sf<T>(query: string, variables: Record<string, any> = {}): Promise<T> {
  const shop = import.meta.env.VITE_SHOPIFY_STORE_DOMAIN;
  const ver = import.meta.env.VITE_STOREFRONT_API_VERSION || "2025-01";
  const token = import.meta.env.VITE_STOREFRONT_API_TOKEN;
  const res = await fetch(`https://${shop}/api/${ver}/graphql.json`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Shopify-Storefront-Access-Token": token,
    },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) throw new Error(JSON.stringify(json.errors));
  return json.data;
}
