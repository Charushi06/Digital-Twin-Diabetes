import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle2, ChevronRight, Users, ShieldAlert, Heart } from 'lucide-react';

export default function PanelView({ patients, selectedPid, onSelectPatient }) {
  const [filterGroup, setFilterGroup] = useState('all');

  const filtered = patients.filter(p => {
    if (filterGroup === 'all') return true;
    return p.group === filterGroup;
  });

  const getRiskLabel = (prob) => {
    if (prob >= 0.45) return { text: "High Risk", pill: "pill-rose", barColor: "var(--soothing-rose)" };
    if (prob >= 0.20) return { text: "Moderate", pill: "pill-amber", barColor: "var(--soothing-amber)" };
    return { text: "Low Risk", pill: "pill-green", barColor: "var(--soothing-green)" };
  };

  return (
    <div className="app-card" style={{ marginBottom: '1.75rem' }}>
      {/* Panel Title & Filters */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--text-title)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Users size={24} color="var(--sea-blue)" />
            <span>Monitored Patients Overview</span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '500' }}>
              ({filtered.length} individuals • Sorted by 2-hour excursion risk)
            </span>
          </h2>
          <div style={{ fontSize: '0.92rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Identifies which individuals are most likely to experience a glucose spike above 180 mg/dL in the next 2 hours.
          </div>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '8px', background: 'var(--bg-subtle)', padding: '5px', borderRadius: '12px', border: '1px solid var(--border-card)' }}>
          {[
            { id: 'all', label: 'All Patients' },
            { id: 'healthy', label: 'Healthy (Normoglycemic)' },
            { id: 'prediabetes', label: 'Prediabetes' },
            { id: 'type2', label: 'Type 2 Diabetes' }
          ].map(g => (
            <button
              key={g.id}
              onClick={() => setFilterGroup(g.id)}
              style={{
                background: filterGroup === g.id ? '#ffffff' : 'transparent',
                color: filterGroup === g.id ? 'var(--sea-blue-dark)' : 'var(--text-muted)',
                boxShadow: filterGroup === g.id ? 'var(--shadow-sm)' : 'none',
                border: filterGroup === g.id ? '1px solid var(--border-card)' : 'none',
                borderRadius: '8px',
                padding: '6px 14px',
                fontSize: '0.85rem',
                fontWeight: '700'
              }}
            >
              {g.label}
            </button>
          ))}
        </div>
      </div>

      {/* Patient Cards / Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 8px', fontSize: '0.92rem' }}>
          <thead>
            <tr style={{ color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: '0.78rem', letterSpacing: '0.04em' }}>
              <th style={{ padding: '8px 16px', textAlign: 'left' }}>Patient ID</th>
              <th style={{ padding: '8px 16px', textAlign: 'left' }}>Health Group</th>
              <th style={{ padding: '8px 16px', textAlign: 'left' }}>Current Glucose</th>
              <th style={{ padding: '8px 16px', textAlign: 'left' }}>Trend (30 min)</th>
              <th style={{ padding: '8px 16px', textAlign: 'left', minWidth: '220px' }}>2-Hour Spike Risk</th>
              <th style={{ padding: '8px 16px', textAlign: 'left' }}>Status Flags</th>
              <th style={{ padding: '8px 16px', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(p => {
              const isSelected = p.pid === selectedPid;
              const riskInfo = getRiskLabel(p.risk_120);

              return (
                <tr 
                  key={p.pid}
                  onClick={() => onSelectPatient(p.pid)}
                  style={{
                    background: isSelected ? 'var(--bg-highlight)' : '#ffffff',
                    boxShadow: 'var(--shadow-sm)',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {/* ID */}
                  <td style={{ padding: '14px 16px', fontWeight: '800', color: 'var(--text-title)', borderTopLeftRadius: '12px', borderBottomLeftRadius: '12px', border: '1px solid var(--border-card)', borderRight: 'none' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: isSelected ? 'var(--sea-blue)' : '#cbd5e1' }} />
                      <span>{p.pid}</span>
                    </div>
                  </td>

                  {/* Group */}
                  <td style={{ padding: '14px 16px', borderTop: '1px solid var(--border-card)', borderBottom: '1px solid var(--border-card)' }}>
                    <span className={`status-pill ${p.group === 'healthy' ? 'pill-green' : (p.group === 'prediabetes' ? 'pill-amber' : 'pill-rose')}`}>
                      {p.group === 'type2' ? 'Type 2 Diabetes' : (p.group.charAt(0).toUpperCase() + p.group.slice(1))}
                    </span>
                  </td>

                  {/* Glucose */}
                  <td style={{ padding: '14px 16px', fontWeight: '700', fontSize: '1rem', borderTop: '1px solid var(--border-card)', borderBottom: '1px solid var(--border-card)' }}>
                    <span style={{ color: p.latest_glucose > 180 ? 'var(--soothing-rose)' : (p.latest_glucose < 70 ? 'var(--soothing-amber)' : 'var(--text-title)') }}>
                      {p.latest_glucose} mg/dL
                    </span>
                  </td>

                  {/* Trend */}
                  <td style={{ padding: '14px 16px', borderTop: '1px solid var(--border-card)', borderBottom: '1px solid var(--border-card)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {p.trend === 'rising' && <TrendingUp size={18} color="var(--soothing-rose)" />}
                      {p.trend === 'falling' && <TrendingDown size={18} color="var(--soothing-green)" />}
                      {p.trend === 'steady' && <Minus size={18} color="var(--text-muted)" />}
                      <span style={{ fontWeight: '600', color: p.trend === 'rising' ? 'var(--soothing-rose)' : (p.trend === 'falling' ? 'var(--soothing-green)' : 'var(--text-body)') }}>
                        {p.glucose_delta_30 > 0 ? `+${p.glucose_delta_30}` : p.glucose_delta_30} mg/dL
                      </span>
                    </div>
                  </td>

                  {/* Risk */}
                  <td style={{ padding: '14px 16px', borderTop: '1px solid var(--border-card)', borderBottom: '1px solid var(--border-card)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className={`status-pill ${riskInfo.pill}`} style={{ minWidth: '70px', justifyContent: 'center' }}>
                        {(p.risk_120 * 100).toFixed(0)}%
                      </span>
                      <div style={{ flex: 1, height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.min(100, p.risk_120 * 100)}%`, height: '100%', background: riskInfo.barColor, borderRadius: '4px' }} />
                      </div>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {riskInfo.text}
                      </span>
                    </div>
                  </td>

                  {/* Flags */}
                  <td style={{ padding: '14px 16px', borderTop: '1px solid var(--border-card)', borderBottom: '1px solid var(--border-card)' }}>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {p.currently_high && (
                        <span className="status-pill pill-rose" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>
                          <AlertCircle size={12} /> Currently High (&gt;180)
                        </span>
                      )}
                      {p.is_warmed_up ? (
                        <span className="status-pill pill-green" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>
                          <CheckCircle2 size={12} /> Twin Ready
                        </span>
                      ) : (
                        <span className="status-pill pill-amber" style={{ fontSize: '0.75rem', padding: '2px 8px' }}>
                          Calibrating
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Action */}
                  <td style={{ padding: '14px 16px', textAlign: 'right', borderTopRightRadius: '12px', borderBottomRightRadius: '12px', border: '1px solid var(--border-card)', borderLeft: 'none' }}>
                    <button
                      onClick={(e) => { e.stopPropagation(); onSelectPatient(p.pid); }}
                      style={{
                        background: isSelected ? 'var(--sea-blue)' : 'var(--bg-subtle)',
                        color: isSelected ? '#ffffff' : 'var(--text-body)',
                        border: '1px solid var(--border-card)',
                        padding: '8px 16px',
                        fontSize: '0.85rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        boxShadow: isSelected ? '0 2px 8px rgba(2, 132, 199, 0.3)' : 'none'
                      }}
                    >
                      {isSelected ? 'Viewing' : 'Inspect'} <ChevronRight size={15} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
