// Dev-only page for simulating tag scans
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './devscan.css'

type Template = {
  id: string
  athlete_name: string
  version: string
  template_code: string
  minted_count: number
  edition_cap: number
}

export default function DevScan() {
  const navigate = useNavigate()
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    fetchTemplates()
  }, [])

  async function fetchTemplates() {
    try {
      const base = import.meta.env.VITE_API_BASE_URL || ''
      const r = await fetch(`${base}/api/scan/dev/templates`, { credentials: 'include' })
      if (!r.ok) throw new Error('Failed to fetch templates')
      const data = await r.json()
      setTemplates(data.templates || [])
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function simulateScan(templateId: string) {
    setScanning(true)
    setError(null)

    try {
      const base = import.meta.env.VITE_API_BASE_URL || ''
      const r = await fetch(`${base}/api/scan/dev/fake-scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ 
          template_id: templateId,
          force_new: true 
        })
      })

      const data = await r.json()

      if (!r.ok || !data.ok) {
        throw new Error(data.reason || 'Scan failed')
      }

      // Show success message
      console.log('✅ Fake scan successful:', data)
      setSuccess(`Card #${data.serial_no} minted!`)
      
      // Refresh templates to show updated minted count
      await fetchTemplates()
      
      // Wait a bit to show the updated count, then redirect
      setTimeout(() => {
        setSuccess(null)
        if (data.minted) {
          // First scan - show registered message
          navigate(`/scan/registered?card=${data.cardId}`)
        } else {
          // Subsequent scan - go directly to card
          navigate(`/cards/${data.cardId}`)
        }
      }, 1000)
    } catch (e: any) {
      setError(e.message || 'Failed to simulate scan')
      setScanning(false)
    }
  }

  if (loading) {
    return (
      <div className="dev-scan-page">
        <div className="dev-container">
          <p>Loading templates...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="dev-scan-page">
      <div className="dev-container">
        <div className="dev-header">
          <h1>🔧 Dev: Simulate Tag Scan</h1>
          <p className="dev-subtitle">Click a template to mint a new card with random tag data</p>
        </div>

        {error && (
          <div className="dev-error">
            ❌ {error}
          </div>
        )}

        {success && (
          <div className="dev-success">
            ✅ {success}
          </div>
        )}

        {templates.length === 0 ? (
          <div className="dev-empty">
            <p>No templates found. Create templates first in the admin panel.</p>
          </div>
        ) : (
          <div className="dev-templates">
            {templates.map(t => (
              <div key={t.id} className="dev-template-card">
                <div className="dev-template-info">
                  <h3>{t.athlete_name}</h3>
                  <div className="dev-template-meta">
                    <span className="dev-badge">{t.version}</span>
                    <span className="dev-code">{t.template_code}</span>
                  </div>
                  <p className="dev-minted">
                    Minted: {t.minted_count} / {t.edition_cap || '∞'}
                  </p>
                </div>
                <button
                  className="dev-scan-btn"
                  onClick={() => simulateScan(t.id)}
                  disabled={scanning}
                >
                  {scanning ? '⏳ Scanning...' : '📱 Scan Tag'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

