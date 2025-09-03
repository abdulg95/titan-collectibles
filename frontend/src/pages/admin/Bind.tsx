import { useEffect, useState } from 'react'

type TemplateRow = { id: string; version: 'regular' | 'diamond' }

export default function AdminBind() {
  const [templates, setTemplates] = useState<TemplateRow[]>([])
  const [templateId, setTemplateId] = useState<string>('')
  const [tagId, setTagId] = useState('')
  const [enc, setEnc] = useState('')
  const [eCode, setECode] = useState('')
  const [cmac, setCmac] = useState('')
  const [tt, setTt] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  // admin token + persistence
  const [token, setToken] = useState<string>(localStorage.getItem('admin_token') || '')
  function saveToken() {
    localStorage.setItem('admin_token', token)
    // refresh template list after saving
    loadTemplates().catch(() => {})
  }

  // point to Flask API (e.g., http://10.0.0.127:5001)
  const API = import.meta.env.VITE_API_BASE_URL || ''

  async function authedFetch(path: string, init: RequestInit = {}) {
    const url = new URL(path, API).toString()
    const headers = new Headers(init.headers || {})
    if (token) headers.set('X-Admin-Token', token)
    const r = await fetch(url, { ...init, headers, credentials: 'include' })
    if (r.status === 401) throw new Error('Unauthorized')
    return r
  }

  async function loadTemplates() {
    setLoading(true)
    try {
      const r = await authedFetch('/api/admin/templates')
      const j = await r.json()
      setTemplates(j)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // load whenever token changes so a newly entered token takes effect
    loadTemplates().catch(err => {
      console.error('Load templates failed', err)
      setLoading(false)
    })
  }, [token])

  async function bind() {
    const body: any = { templateId }
    if (tagId && eCode && enc && (cmac || tt)) {
      body.tagId = tagId
      body.eCode = eCode
      body.enc = enc
      if (tt) body.tt = tt
      else body.cmac = cmac
    } else {
      alert('Enter tagId, eCode, enc and cmac (or tt) from a scan URL.')
      return
    }

    try {
      const r = await authedFetch('/api/admin/bind', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      })
      const j = await r.json()
      setResult(j)
      // optional: reload templates to see minted_count update
      loadTemplates().catch(() => {})
    } catch (e: any) {
      alert(e?.message || 'Bind failed')
    }
  }

  if (loading) return <p style={{ padding: 24 }}>Loading…</p>

  return (
    <div style={{ padding: 24, display: 'grid', gap: 24, maxWidth: 900 }}>
      <h1>Bind by Scan</h1>
      <div style={{ margin: '12px 0' }}>
        <label>
          Admin Token:{' '}
          <input value={token} onChange={(e) => setToken(e.target.value)} />
        </label>{' '}
        <button onClick={saveToken}>Save</button>
      </div>

      <p>
        Paste parameters from a scanned URL (<code>tagId</code>, <code>enc</code>,{' '}
        <code>eCode</code>, and <code>cmac</code> <em>or</em> <code>tt</code>), choose
        the correct template, then click <strong>Bind</strong>.
      </p>

      <label>
        Template:
        <select
          value={templateId}
          onChange={(e) => setTemplateId(e.target.value)}
          style={{ marginLeft: 8 }}
        >
          <option value="">-- select --</option>
          {templates.map((t) => (
            <option key={t.id} value={t.id}>
              {t.id} — {t.version}
            </option>
          ))}
        </select>
      </label>

      <label>
        tagId <input value={tagId} onChange={(e) => setTagId(e.target.value)} style={{ width: '100%' }} />
      </label>
      <label>
        enc <input value={enc} onChange={(e) => setEnc(e.target.value)} style={{ width: '100%' }} />
      </label>
      <label>
        eCode <input value={eCode} onChange={(e) => setECode(e.target.value)} style={{ width: '100%' }} />
      </label>
      <label>
        cmac{' '}
        <input
          value={cmac}
          onChange={(e) => setCmac(e.target.value)}
          style={{ width: '100%' }}
          placeholder="or use tt below"
        />
      </label>
      <label>
        tt{' '}
        <input
          value={tt}
          onChange={(e) => setTt(e.target.value)}
          style={{ width: '100%' }}
          placeholder="if tamper mode used"
        />
      </label>

      <button onClick={bind} disabled={!templateId}>
        Bind
      </button>

      {result && <pre style={{ background: '#f6f6f6', padding: 12 }}>{JSON.stringify(result, null, 2)}</pre>}

      <div>
        <a href="/admin/templates">Back to Templates</a>
      </div>
    </div>
  )
}
