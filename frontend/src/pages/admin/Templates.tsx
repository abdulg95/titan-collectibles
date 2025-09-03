import { useEffect, useState } from 'react'

type TemplateRow = {
  id: string
  version: 'regular' | 'diamond'
  athlete_id: string
  glb_url?: string
  image_url?: string
  minted_count: number
  edition_cap?: number | null
  etrnl_url_group_id?: string | null
}

export default function AdminTemplates(){
  const [rows, setRows] = useState<TemplateRow[]>([])
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState<string>(localStorage.getItem('admin_token') || '')

  // Point to your Flask backend (e.g., http://10.0.0.127:5001)
  const API = import.meta.env.VITE_API_BASE_URL || ''

  async function authedFetch(path: string, init: RequestInit = {}) {
    const url = new URL(path, API).toString()
    const headers = new Headers(init.headers || {})
    if (token) headers.set('X-Admin-Token', token)
    const r = await fetch(url, { ...init, headers, credentials: 'include' })
    if (r.status === 401) throw new Error('Unauthorized')
    return r
  }

  function saveToken() {
    localStorage.setItem('admin_token', token)
    // refetch after saving token
    setLoading(true)
    authedFetch('/api/admin/templates')
      .then(r => r.json())
      .then(j => setRows(j))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    (async () => {
      try {
        const r = await authedFetch('/api/admin/templates')
        const j = await r.json()
        setRows(j)
      } finally {
        setLoading(false)
      }
    })()
    // re-run when token changes so a newly entered token takes effect
  }, [token])

  if (loading) return <p style={{ padding: 24 }}>Loading templates…</p>

  return (
    <div style={{ padding: 24 }}>
      <div style={{ margin: '12px 0' }}>
        <label>
          Admin Token:{' '}
          <input value={token} onChange={e => setToken(e.target.value)} />
        </label>{' '}
        <button onClick={saveToken}>Save</button>
      </div>

      <h1>Templates</h1>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th align="left">Template ID</th>
            <th align="left">Version</th>
            <th align="right">Minted</th>
            <th align="left">ETRNL Group</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(r => (
            <tr key={r.id} style={{ borderTop: '1px solid #ddd' }}>
              <td>{r.id}</td>
              <td>{r.version}</td>
              <td align="right">
                {r.minted_count}
                {r.edition_cap ? ` / ${r.edition_cap}` : ''}
              </td>
              <td>{r.etrnl_url_group_id || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: 24 }}>
        <a href="/admin/bind">Go to “Bind by Scan”</a>
      </div>
    </div>
  )
}
