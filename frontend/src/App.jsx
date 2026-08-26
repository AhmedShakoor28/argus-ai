import { useState, useRef, useCallback, useEffect } from 'react'

/* ═══════════════════════════════════════════
   SVG Icon components (inline for zero deps)
   ═══════════════════════════════════════════ */

const Icon = ({ children, size = 20, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size}
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...props}>
    {children}
  </svg>
)

const HomeIcon = (p) => <Icon {...p}><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/><polyline points="9 22 9 12 15 12 15 22"/></Icon>
const BarChartIcon = (p) => <Icon {...p}><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></Icon>
const HistoryIcon = (p) => <Icon {...p}><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></Icon>
const SettingsIcon = (p) => <Icon {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></Icon>
const UploadCloudIcon = (p) => <Icon {...p}><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></Icon>
const MapPinIcon = (p) => <Icon size={14} {...p}><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></Icon>
const CrosshairIcon = (p) => <Icon size={18} {...p}><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></Icon>
const FlameIcon = (p) => <Icon size={14} {...p}><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></Icon>
const MountainIcon = (p) => <Icon size={14} {...p}><path d="M8 3l4 8 5-5 5 15H2L8 3z"/></Icon>
const LayersIcon = (p) => <Icon size={14} {...p}><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></Icon>

// Pipeline icons
const SearchIcon = (p) => <Icon size={16} {...p}><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></Icon>
const CheckCircleIcon = (p) => <Icon size={16} {...p}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></Icon>
const ZapIcon = (p) => <Icon size={16} {...p}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></Icon>
const FileTextIcon = (p) => <Icon size={16} {...p}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></Icon>

// Feature icons
const CpuIcon = (p) => <Icon size={22} {...p}><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></Icon>
const ShieldCheckIcon = (p) => <Icon size={22} {...p}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></Icon>
const BoltIcon = (p) => <Icon size={22} {...p}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></Icon>
const ClipboardIcon = (p) => <Icon size={22} {...p}><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><line x1="8" y1="12" x2="16" y2="12"/><line x1="8" y1="16" x2="12" y2="16"/></Icon>
const HelpCircleIcon = (p) => <Icon {...p}><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></Icon>
const DownloadIcon = (p) => <Icon size={16} {...p}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></Icon>
const AlertTriangleIcon = (p) => <Icon size={16} {...p}><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></Icon>

/* ═══════════════════════
   Clock Hook
   ═══════════════════════ */
function useClock() {
  const [time, setTime] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  return time
}

/* ═══════════════════════
   Sidebar
   ═══════════════════════ */
function Sidebar() {
  const [active, setActive] = useState('home')

  const navItems = [
    { id: 'home', icon: HomeIcon, label: 'Home' },
    { id: 'analytics', icon: BarChartIcon, label: 'Analytics' },
    { id: 'history', icon: HistoryIcon, label: 'History' },
  ]

  return (
    <aside className="sidebar" id="sidebar-nav">
      <div className="sidebar-logo" title="Argus-AI">
        <div className="dot" />
      </div>

      <nav className="sidebar-nav">
        {navItems.map(item => (
          <button
            key={item.id}
            id={`nav-${item.id}`}
            className={`sidebar-btn ${active === item.id ? 'active' : ''}`}
            onClick={() => setActive(item.id)}
            title={item.label}
          >
            <item.icon />
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <button className="sidebar-btn" id="nav-settings" title="Settings">
          <SettingsIcon />
        </button>
        <button className="sidebar-btn" id="nav-help" title="Help">
          <HelpCircleIcon />
        </button>
      </div>
    </aside>
  )
}

/* ═══════════════════════
   Top Header Bar
   ═══════════════════════ */
function TopBar() {
  const time = useClock()
  const timeStr = time.toISOString().slice(11, 19) + ' UTC'

  return (
    <header className="top-bar" id="top-bar">
      <div className="top-bar-left">
        <div>
          <div className="top-bar-title">
            ARGUS<span>-AI</span>
          </div>
          <div className="top-bar-subtitle">Disaster Detection Command</div>
        </div>
      </div>
      <div className="top-bar-right">
        <div className="system-status" id="system-status">
          <span className="live-dot" />
          SYSTEM ONLINE
        </div>
        <span className="utc-time">{timeStr}</span>
      </div>
    </header>
  )
}

/* ═══════════════════════
   Dropzone
   ═══════════════════════ */
function Dropzone({ file, onFile, disabled }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)
  const previewUrl = file ? URL.createObjectURL(file) : null

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files?.[0]
    if (f) onFile(f)
  }, [onFile])

  return (
    <div
      id="dropzone"
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
            onClick={() => !disabled && inputRef.current?.click()}
      style={{ pointerEvents: disabled ? 'none' : 'auto', opacity: disabled ? 0.6 : 1 }}
      className={`dropzone-card ${dragging ? 'dragging' : ''}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        style={{ display: 'none' }}
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />

      {!file && <div className="scanline" style={{ top: 0 }} />}

      {previewUrl ? (
        <img src={previewUrl} alt="Selected input" className="dropzone-preview" />
      ) : (
        <>
          <div className="dropzone-icon">
            <UploadCloudIcon />
          </div>
          <p className="dropzone-title">
            Drag & drop aerial or ground imagery here
          </p>
          <p className="dropzone-hint">or click to browse</p>
          <p className="dropzone-meta">.JPG / .PNG &middot; Max size: 25MB</p>
        </>
      )}
    </div>
  )
}

/* ═══════════════════════
   Pipeline Indicator
   ═══════════════════════ */
function Pipeline({ status }) {
  const steps = [
    { icon: SearchIcon, label: 'Detection' },
    { icon: CheckCircleIcon, label: 'Verification' },
    { icon: ZapIcon, label: 'Response' },
    { icon: FileTextIcon, label: 'Report' },
  ]

  const [activeStep, setActiveStep] = useState(-1)

  useEffect(() => {
    if (status !== 'running') {
      if (status === 'done') setActiveStep(steps.length)
      else if (status === 'idle') setActiveStep(-1)
      return
    }
    setActiveStep(0)
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev))
    }, 3000)
    return () => clearInterval(interval)
  }, [status])

  return (
    <div className="pipeline" id="pipeline-steps">
      {steps.map((step, i) => {
        const isDone = activeStep > i || status === 'done'
        const isCurrent = activeStep === i && status === 'running'
        const color = isDone ? '#2dd4bf' : isCurrent ? '#5eead4' : undefined

        return (
          <div key={step.label} style={{ display: 'flex', alignItems: 'center' }}>
            <div className="pipeline-step">
              <div
                className="pipeline-step-icon"
                style={{
                  borderColor: color,
                  color: color,
                  boxShadow: isCurrent ? '0 0 12px rgba(45,212,191,0.5)' : undefined,
                  transition: 'all .3s',
                }}
              >
                <step.icon />
              </div>
              <span className="pipeline-step-label">{step.label}</span>
            </div>
            {i < steps.length - 1 && (
              <div
                className="pipeline-connector"
                style={{
                  background: activeStep > i ? '#2dd4bf' : undefined,
                  transition: 'background .3s',
                }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}

/* ═══════════════════════
   Feature Cards
   ═══════════════════════ */
function Features() {
  const cards = [
    { icon: CpuIcon, cls: 'detection', title: 'AI Detection', desc: 'Advanced models identify threats accurately' },
    { icon: ShieldCheckIcon, cls: 'verification', title: 'Cross-Verification', desc: 'Multi-source data ensures reliable verification' },
    { icon: BoltIcon, cls: 'response', title: 'Smart Response', desc: 'AI generates actionable recommendations' },
    { icon: ClipboardIcon, cls: 'report', title: 'Detailed Report', desc: 'Comprehensive PDF report with evidence & next steps' },
  ]

  return (
    <section className="features-section" id="features">
      <div className="features-grid">
        {cards.map((card, i) => (
          <div key={card.title} className={`feature-card animate-in animate-delay-${i + 1}`}>
            <div className={`feature-icon ${card.cls}`}>
              <card.icon />
            </div>
            <div className="feature-text">
              <h3>{card.title}</h3>
              <p>{card.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ═══════════════════════
   Results Panel
   ═══════════════════════ */

// Normalize whatever shape the backend returns into a flat array of
// per-disaster-type result objects. Handles: report.results = {fire:{...}, landslide:{...}},
// report.detections = [...], or a single flat object (one detection type only).
function normalizeDetections(report) {
  if (!report) return []
  if (Array.isArray(report.detections)) return report.detections
  if (report.results && typeof report.results === 'object') {
    return Object.entries(report.results).map(([type, r]) => ({ detection_type: type, ...r }))
  }
  if (report.detection_type) return [report]
  // last resort: any top-level keys that look like disaster types
  const known = ['fire', 'landslide', 'smoke']
  const found = known.filter((k) => report[k] && typeof report[k] === 'object')
  if (found.length) return found.map((k) => ({ detection_type: k, ...report[k] }))
  return []
}

function StatusBadge({ status }) {
  const s = (status || '').toLowerCase()
  const confirmed = s.includes('confirm') && !s.includes('un')
  const color = confirmed ? '#2dd4bf' : s.includes('unconfirm') ? '#fbbf24' : '#94a3b8'
  return (
    <span
      style={{
        color,
        borderColor: color,
        fontSize: '11px',
        fontWeight: 700,
        letterSpacing: '0.06em',
        padding: '3px 10px',
        border: '1px solid',
        borderRadius: '999px',
        textTransform: 'uppercase',
      }}
    >
      {status || 'unknown'}
    </span>
  )
}

function DetectionCard({ det }) {
  const type = det.detection_type || 'detection'
  const status = det.result_status
  const verification = det.verification || {}
  const weather = verification.weather
  const verificationNotes = verification.reasons
  const cautionFlags = det.caution_flags
  const recommendation = det.response?.recommendation
  const sources = det.response?.sources

  return (
    <div
      style={{
        background: '#0d1420',
        border: '1px solid #1e293b',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '16px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h3 style={{ color: '#e2e8f0', fontSize: '16px', fontWeight: 700, textTransform: 'capitalize' }}>
          {type}
        </h3>
        <StatusBadge status={status} />
      </div>

      {weather && (
        <p style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '8px' }}>
          Weather: {weather.condition} ({weather.description}), {weather.temp_c}°C, {weather.humidity}% humidity,{' '}
          {weather.rain_last_hour_mm}mm rain (last hr)
        </p>
      )}

      {cautionFlags && cautionFlags.length > 0 && (
        <div style={{ display: 'flex', gap: '6px', alignItems: 'flex-start', color: '#fbbf24', fontSize: '13px', marginBottom: '10px' }}>
          <AlertTriangleIcon style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>{cautionFlags.join('; ')}</span>
        </div>
      )}

      {verificationNotes && verificationNotes.length > 0 && (
        <p style={{ color: '#64748b', fontSize: '12px', marginBottom: '10px' }}>
          Verification notes: {Array.isArray(verificationNotes) ? verificationNotes.join('; ') : verificationNotes}
        </p>
      )}

      {recommendation && (
        <details style={{ marginTop: '8px' }}>
          <summary style={{ color: '#2dd4bf', fontSize: '13px', cursor: 'pointer', fontWeight: 600 }}>
            Recommended Response
          </summary>
          <p style={{ color: '#cbd5e1', fontSize: '13px', lineHeight: 1.6, whiteSpace: 'pre-wrap', marginTop: '8px' }}>
            {recommendation}
          </p>
        </details>
      )}

      {sources && sources.length > 0 && (
        <p style={{ color: '#64748b', fontSize: '11px', marginTop: '10px' }}>
          Sources: {[...new Set(sources)].join(', ')}
        </p>
      )}
    </div>
  )
}

function ResultsPanel({ result, error, status, onReset }) {
  if (status === 'error') {
    return (
      <section style={{ maxWidth: '900px', margin: '0 auto', padding: '0 24px 40px' }}>
        <div style={{ background: '#1c0f0f', border: '1px solid #7f1d1d', borderRadius: '12px', padding: '20px', color: '#fca5a5' }}>
          Analysis failed: {error}
        </div>
      </section>
    )
  }

  if (status !== 'done' || !result) return null

  const detections = normalizeDetections(result)
  const pdfUrl = result.pdf_url ? `http://127.0.0.1:8000${result.pdf_url}` : null

  return (
    <section style={{ maxWidth: '900px', margin: '0 auto', padding: '0 24px 40px' }} id="results-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ color: '#e2e8f0', fontSize: '20px', fontWeight: 700 }}>Analysis Results</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          {pdfUrl && (
            <a
              href={pdfUrl}
              target="_blank"
              rel="noreferrer"
              style={{
                display: 'flex', alignItems: 'center', gap: '6px',
                color: '#0f172a', background: '#2dd4bf',
                fontSize: '13px', fontWeight: 700, padding: '8px 14px',
                borderRadius: '8px', textDecoration: 'none',
              }}
            >
              <DownloadIcon /> Download PDF
            </a>
          )}
          {onReset && (
            <button
              onClick={onReset}
              style={{
                color: '#94a3b8', background: 'transparent',
                border: '1px solid #334155', fontSize: '13px', fontWeight: 600,
                padding: '8px 14px', borderRadius: '8px', cursor: 'pointer',
              }}
            >
              New Analysis
            </button>
          )}
        </div>
      </div>

      {detections.length === 0 ? (
        result.triggered_types && result.triggered_types.length === 0 ? (
          <div
            style={{
              background: '#0d1420', border: '1px solid #1e293b', borderRadius: '12px',
              padding: '32px', textAlign: 'center', color: '#94a3b8',
            }}
          >
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>✓</div>
            <p style={{ color: '#e2e8f0', fontWeight: 600, marginBottom: '4px' }}>No threats detected</p>
            <p style={{ fontSize: '13px' }}>Image analyzed clean — no fire or landslide signals found.</p>
          </div>
        ) : (
          <pre style={{ color: '#94a3b8', fontSize: '12px', background: '#0d1420', padding: '16px', borderRadius: '8px', overflowX: 'auto' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        )
      ) : (
        detections.map((det, i) => <DetectionCard key={i} det={det} />)
      )}
    </section>
  )
}

/* ═══════════════════════
   Main App
   ═══════════════════════ */
export default function App() {
  const [file, setFile] = useState(null)
  const [city, setCity] = useState('')
  const [mode, setMode] = useState('both')
  const [status, setStatus] = useState('idle') // idle | running | done | error
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const canRun = file && city.trim().length > 0 && status !== 'running'

  const handleRun = async () => {
    if (!canRun) return
    setStatus('running')
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('city', city)
      formData.append('mode', mode)

      const res = await fetch('/api/analyze', { method: 'POST', body: formData })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Request failed (${res.status})`)
      }

      const data = await res.json()
      setResult(data)
      setStatus('done')
    } catch (e) {
      setError(e.message)
      setStatus('error')
    }
  }

  const handleReset = () => {
    setFile(null)
    setCity('')
    setMode('both')
    setStatus('idle')
    setResult(null)
    setError(null)
  }

  const modes = [
    { id: 'fire', label: 'Fire', icon: FlameIcon },
    { id: 'landslide', label: 'Landslide', icon: MountainIcon },
    { id: 'both', label: 'Both', icon: LayersIcon },
  ]

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-content">
        <TopBar />

        <section className="hero-section" id="hero">
          <div className="hero-bg">
            <img src="/hero-bg.png" alt="" aria-hidden="true" />
          </div>

          <div className="hero-inner">
            <div className="hero-left">
              <div>
                <p className="hero-badge">New Analysis</p>
                <h2 className="hero-heading">
                  Detect. Verify. Respond.
                  <span className="accent">Save Lives.</span>
                </h2>
                <p className="hero-desc">
                  Upload aerial or ground imagery. Argus-AI analyzes real-time
                  data and delivers actionable disaster intelligence.
                </p>
              </div>

              <div className="form-grid">
                  <Dropzone file={file} onFile={setFile} disabled={status === 'running'} />

                <div className="controls-panel">
                  <div className="field-group">
                    <label><MapPinIcon /> Location</label>
                    <div className="location-input-wrap">
                <input
                  id="location-input"
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="e.g. Rawalpindi, Pakistan"
                  className="location-input"
                  disabled={status === 'running'}
                />
                      <button className="location-detect-btn" title="Detect location" id="detect-location-btn">
                        <CrosshairIcon />
                      </button>
                    </div>
                  </div>

                  <div className="field-group">
                    <label>Detection Mode</label>
                    <div className="mode-group" id="mode-selector">
                      {modes.map((m) => (
                        <button
                          key={m.id}
                          id={`mode-${m.id}`}
                          type="button"
                          onClick={() => setMode(m.id)}
                          disabled={status === 'running'}
                          className={`mode-btn ${mode === m.id ? 'active' : ''}`}
                        >
                          <m.icon /> {m.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    id="run-analysis-btn"
                    onClick={handleRun}
                    disabled={!canRun}
                    className={`run-btn ${canRun ? 'enabled' : 'disabled'}`}
                  >
                    {status === 'running' ? 'ANALYZING…' : 'RUN ANALYSIS'}
                    <span className="arrow">→</span>
                  </button>

                  <Pipeline status={status} />
                </div>
              </div>
            </div>

            <div className="hero-right">
              <div className="legend-item"><span className="legend-dot fire" />Fire Detected</div>
              <div className="legend-item"><span className="legend-dot landslide" />Landslide Risk</div>
              <div className="legend-item"><span className="legend-dot smoke" />Smoke Detected</div>
            </div>
          </div>
        </section>

        <ResultsPanel result={result} error={error} status={status} onReset={handleReset} />

        <Features />

        <footer className="footer-tagline" id="footer">
          Empowering Faster Decisions. Saving Lives.
        </footer>
      </div>
    </div>
  )
}