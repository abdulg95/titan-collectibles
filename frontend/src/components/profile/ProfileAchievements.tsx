// src/components/profile/ProfileAchievements.tsx
type Props = {
    totalCollected: number
    goal?: number
  }
  
  export default function ProfileAchievements({ totalCollected, goal = 8 }: Props) {
    const clamped = Math.max(0, Math.min(goal, totalCollected))
    const pct = clamped / goal
  
    const size = 96
    const stroke = 10
    const r = (size - stroke) / 2
    const c = 2 * Math.PI * r
    const dash = c * pct
    const unlocked = clamped >= goal

  
    return (
      <div className="achv-card" aria-labelledby="achv-title">
        <div className="achv-head">
          <div id="achv-title" className="achv-title">Achievements</div>
          <div className="achv-sub">World Archery Series 1</div>
        </div>
  
        <div className="achv-body">
          <div className="achv-ring-wrap" aria-label={`${clamped} of ${goal} cards collected`}>
            <svg
              className="achv-ring"
              width={size}
              height={size}
              viewBox={`0 0 ${size} ${size}`}
            >
              <circle
                className="achv-ring__track"
                cx={size / 2}
                cy={size / 2}
                r={r}
                strokeWidth={stroke}
                fill="none"
              />
              <circle
                className="achv-ring__progress"
                cx={size / 2}
                cy={size / 2}
                r={r}
                strokeWidth={stroke}
                fill="none"
                strokeDasharray={`${dash} ${c - dash}`}
                strokeLinecap="round"
                transform={`rotate(-90 ${size / 2} ${size / 2})`}
              />
              <text
                className="achv-ring__label"
                x="50%"
                y="50%"
                dominantBaseline="middle"
                textAnchor="middle"
              >
                {clamped}/{goal}
              </text>
            </svg>
            <div className="achv-caption">Cards collected</div>
          </div>
  
          <div className={`achv-bonus ${unlocked ? 'unlocked' : 'locked'}`}>
            <div className="lock" aria-hidden>
                <svg viewBox="0 0 24 24" width="24" height="24">
                <path d="M7 10V7a5 5 0 0 1 10 0v3" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
                <rect x="5" y="10" width="14" height="10" rx="2.2" ry="2.2" fill="none" stroke="currentColor" strokeWidth="1.8"/>
                <circle cx="12" cy="15" r="1.4" fill="currentColor"/>
                </svg>
            </div>
            <div className="bonus-title">{unlocked ? 'Unlocked' : 'Not collected'}</div>
            <div className="bonus-sub">Bonus card</div>
        </div>
        </div>
      </div>
    )
  }
  