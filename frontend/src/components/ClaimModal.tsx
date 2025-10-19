// src/components/ClaimModal.tsx
import { useEffect } from 'react'
import './claimmodal.css'

type Props = {
  open: boolean
  onClose: () => void
  onConfirm: () => void
  loading?: boolean
}

export default function ClaimModal({ open, onClose, onConfirm, loading }: Props) {
  // Close on ESC key
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape' && open) onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  // Prevent background scroll when modal is open
  useEffect(() => {
    if (open) {
      document.body.classList.add('modal-open')
    } else {
      document.body.classList.remove('modal-open')
    }
    return () => document.body.classList.remove('modal-open')
  }, [open])

  if (!open) return null

  // Click outside to close
  function backdropClick(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) onClose()
  }

  return (
    <div 
      className="claim-modal-overlay" 
      onClick={backdropClick}
      role="dialog" 
      aria-modal="true"
      aria-labelledby="claim-modal-title"
    >
      <div className="claim-modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="claim-modal-header">
          <h2 id="claim-modal-title">Add to collection?</h2>
          <p className="claim-modal-description">
            This will save the card to your personal collection so you can view the digital card anytime. Once you add it, it's yours!
          </p>
        </div>

        <div className="claim-modal-divider" />

        <div className="claim-modal-actions">
          <button
            className="claim-btn-primary"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? 'Adding...' : 'Add to Collection'}
          </button>
          <button
            className="claim-btn-cancel"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}

