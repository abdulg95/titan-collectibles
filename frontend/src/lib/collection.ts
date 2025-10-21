export type CollectionItem = {
    id: string;                 // card instance id
    serial_no: number;
    status: string;
    template: { version: string | null; image_url: string | null; glb_url: string | null };
    athlete: { id: string; full_name: string; slug: string; card_image_url: string | null };
  };
  
  const API = import.meta.env.VITE_API_BASE_URL || '';
  
  export async function fetchMyCollection(): Promise<{ items: CollectionItem[] }> {
    const authToken = localStorage.getItem('auth_token')
    let url = new URL('/api/collection', API).toString()
    
    if (authToken) {
      // Send auth token as query parameter instead of header (Safari blocks Authorization header)
      url += `?auth_token=${encodeURIComponent(authToken)}`
      console.log('🔐 Sending auth token as query parameter for collection:', `${authToken.substring(0, 20)}...`)
    } else {
        console.log('❌ No auth token found in localStorage for collection fetch')
    }
    
    console.log('🌐 Fetching /api/collection with URL:', url)
    const r = await fetch(url, { credentials: 'include' });
    if (r.status === 401) throw new Error('auth');
    if (!r.ok) throw new Error('fetch_failed');
    return r.json();
  }
  