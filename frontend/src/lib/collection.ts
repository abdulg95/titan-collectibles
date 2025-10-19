export type CollectionItem = {
    id: string;                 // card instance id
    serial_no: number;
    status: string;
    template: { version: string | null; image_url: string | null; glb_url: string | null };
    athlete: { id: string; full_name: string; slug: string; card_image_url: string | null };
  };
  
  const API = import.meta.env.VITE_API_BASE_URL || '';
  
  export async function fetchMyCollection(): Promise<{ items: CollectionItem[] }> {
    const r = await fetch(new URL('/api/collection', API).toString(), { credentials: 'include' });
    if (r.status === 401) throw new Error('auth');
    if (!r.ok) throw new Error('fetch_failed');
    return r.json();
  }
  