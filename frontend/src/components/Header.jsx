import React from 'react';
import { Play, Pause, HelpCircle, ShieldCheck, HeartPulse, User } from 'lucide-react';

export default function Header({ 
  patients = [], 
  selectedPid = '', 
  onSelectPid, 
  isPlaying = false, 
  onTogglePlay, 
  playbackSpeed = 1, 
  onChangeSpeed,
  currentTs,
  onOpenTransparency,
  onStartTour
}) {
  return (
    <header 
      className="app-header-bar"
      style={{
        borderBottom: '2px solid #e2e8f0',
        backgroundColor: '#ffffff',
        background: '#ffffff',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        padding: '0.9rem 2rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1.25rem',
        boxShadow: '0 2px 10px rgba(15, 23, 42, 0.05)',
        flexWrap: 'wrap'
      }}
    >
      {/* Brand & Title - Light & Crisp */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          width: '46px',
          height: '46px',
          borderRadius: '14px',
          background: 'linear-gradient(135deg, #0284c7 0%, #6366f1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 14px rgba(2, 132, 199, 0.25)',
          flexShrink: 0
        }}>
          <HeartPulse size={26} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '1.45rem', fontWeight: '800', color: '#0f172a', letterSpacing: '-0.02em' }}>
              GlucoTwin
            </span>
            <span style={{
              background: '#eef2ff',
              color: '#4338ca',
              border: '1px solid #c7d2fe',
              fontSize: '0.75rem',
              fontWeight: '700',
              padding: '3px 10px',
              borderRadius: '999px',
              letterSpacing: '0.02em'
            }}>
              Digital Twin Care
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: '#475569', fontWeight: '500', marginTop: '1px' }}>
            Type 2 Diabetes & CGM Prediction Assistant
          </div>
        </div>
      </div>

      {/* Patient Picker, Replay Bar & Interactive Tour */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem', flexWrap: 'wrap' }}>
        
        {/* Patient Dropdown - Clean White Card */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: '#f8fafc',
          padding: '6px 14px',
          borderRadius: '12px',
          border: '1.5px solid #cbd5e1',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)'
        }}>
          <User size={18} color="#0284c7" />
          <span style={{ fontSize: '0.9rem', color: '#0f172a', fontWeight: '700' }}>Patient:</span>
          <select 
            value={selectedPid} 
            onChange={(e) => onSelectPid && onSelectPid(e.target.value)}
            style={{
              background: '#ffffff',
              color: '#0f172a',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              padding: '5px 10px',
              fontSize: '0.92rem',
              fontWeight: '700',
              outline: 'none',
              cursor: 'pointer',
              minWidth: '230px'
            }}
          >
            {patients.map(p => (
              <option key={p.pid} value={p.pid}>
                {p.pid} — {p.group ? (p.group.charAt(0).toUpperCase() + p.group.slice(1)) : ''} (Risk: {(p.risk_120 * 100).toFixed(0)}%)
              </option>
            ))}
          </select>
        </div>

        {/* Big, Friendly Replay Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: '#f8fafc',
          padding: '6px 10px',
          borderRadius: '12px',
          border: '1.5px solid #cbd5e1'
        }}>
          <button 
            onClick={onTogglePlay}
            style={{
              background: isPlaying ? '#ffe4e6' : '#e0f2fe',
              color: isPlaying ? '#e11d48' : '#0369a1',
              border: `1.5px solid ${isPlaying ? '#fecdd3' : '#bae6fd'}`,
              borderRadius: '9px',
              padding: '7px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.88rem',
              fontWeight: '700',
              cursor: 'pointer'
            }}
          >
            {isPlaying ? <Pause size={16} /> : <Play size={16} />}
            {isPlaying ? 'Pause' : 'Replay Timeline'}
          </button>

          <span style={{ fontSize: '0.82rem', color: '#64748b', fontWeight: '600', marginLeft: '4px' }}>Speed:</span>
          {[1, 60, 300].map(speed => (
            <button
              key={speed}
              onClick={() => onChangeSpeed && onChangeSpeed(speed)}
              style={{
                background: playbackSpeed === speed ? '#0284c7' : '#ffffff',
                color: playbackSpeed === speed ? '#ffffff' : '#334155',
                border: '1px solid ' + (playbackSpeed === speed ? '#0284c7' : '#cbd5e1'),
                borderRadius: '8px',
                padding: '5px 9px',
                fontSize: '0.82rem',
                fontWeight: '700',
                cursor: 'pointer'
              }}
            >
              {speed}x
            </button>
          ))}
        </div>

        {/* Guided Tour Help Button - Lavender Accent */}
        <button
          onClick={onStartTour}
          style={{
            background: '#e0e7ff',
            color: '#4338ca',
            border: '1.5px solid #c7d2fe',
            borderRadius: '12px',
            padding: '8px 16px',
            fontSize: '0.9rem',
            fontWeight: '700',
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            cursor: 'pointer',
            boxShadow: '0 1px 3px rgba(99, 102, 241, 0.15)'
          }}
        >
          <HelpCircle size={18} color="#4338ca" />
          How to Use (Guide)
        </button>

        {/* Clinical Transparency Modal Button */}
        <button
          onClick={onOpenTransparency}
          style={{
            background: '#ffffff',
            color: '#0f172a',
            border: '1.5px solid #cbd5e1',
            borderRadius: '12px',
            padding: '8px 15px',
            fontSize: '0.88rem',
            fontWeight: '700',
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            cursor: 'pointer',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04)'
          }}
        >
          <ShieldCheck size={18} color="#0284c7" />
          Clinical Evidence
        </button>
      </div>
    </header>
  );
}
