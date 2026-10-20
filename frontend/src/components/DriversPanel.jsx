import React from 'react';
import { HelpCircle, ArrowUpRight, ArrowDownRight, Compass, Sparkles } from 'lucide-react';

export default function DriversPanel({ drivers, isLoading }) {
  return (
    <div className="app-card" style={{ height: '100%', borderLeft: '5px solid var(--sea-blue)' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--text-title)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={20} color="var(--sea-blue)" />
          <span>Why is this Risk Predicted?</span>
        </h3>
        <span className="status-pill pill-blue" style={{ fontSize: '0.75rem' }}>
          AI Explanation
        </span>
      </div>

      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: '1.5' }}>
        The artificial intelligence highlights the top biological and behavioral factors currently influencing the patient's glucose forecast:
      </p>

      {isLoading ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Analyzing clinical drivers...
        </div>
      ) : (!drivers || drivers.length === 0) ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Move the timeline slider to view plain-language drivers at that moment.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {drivers.map((d, i) => {
            const isIncrease = d.direction === 'risk_increasing';

            return (
              <div
                key={i}
                style={{
                  background: isIncrease ? 'var(--soothing-rose-light)' : 'var(--soothing-green-light)',
                  border: `1px solid ${isIncrease ? '#fecdd3' : '#a7f3d0'}`,
                  borderRadius: '14px',
                  padding: '1rem 1.25rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '1rem'
                }}
              >
                <div style={{
                  padding: '6px',
                  borderRadius: '10px',
                  background: '#ffffff',
                  color: isIncrease ? 'var(--soothing-rose)' : 'var(--soothing-green)',
                  boxShadow: 'var(--shadow-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginTop: '2px'
                }}>
                  {isIncrease ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-title)', lineHeight: '1.4' }}>
                    {d.sentence}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '6px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>Factor: {d.feature.replace(/_/g, ' ')}</span>
                    <span>•</span>
                    <span style={{ fontWeight: '600', color: isIncrease ? 'var(--soothing-rose)' : 'var(--soothing-green)' }}>
                      {isIncrease ? 'Raises Excursion Risk' : 'Lowers Excursion Risk'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
