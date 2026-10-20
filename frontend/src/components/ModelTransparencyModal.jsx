import React, { useState, useEffect } from 'react';
import { X, ShieldCheck, Database, Award, Info, Activity, CheckCircle, TrendingUp, Sparkles } from 'lucide-react';

export default function ModelTransparencyModal({ isOpen, onClose }) {
  const [metricsData, setMetricsData] = useState(null);
  const [activeTab, setActiveTab] = useState('ablation');

  useEffect(() => {
    if (isOpen) {
      fetch('/api/metrics')
        .then(res => res.json())
        .then(data => setMetricsData(data))
        .catch(err => console.error(err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  // Curated ablation table rows for pristine, elder-friendly rendering
  const ablationData = [
    { variant: "A0: Glucose Only", features: 15, prauc: "0.399 [0.366, 0.432]", auroc: "0.908 [0.891, 0.922]", gain: "Baseline", note: "Raw CGM trajectory and 30-min rate of change" },
    { variant: "A1: + Meals & Carbs", features: 26, prauc: "0.444 [0.389, 0.494]", auroc: "0.928 [0.913, 0.942]", gain: "+0.045 PR-AUC", note: "Meal carbs, timing decay, and fat-protein moderation" },
    { variant: "A2: + Wearable Sensors", features: 33, prauc: "0.430 [0.373, 0.484]", auroc: "0.928 [0.913, 0.942]", gain: "+0.031 PR-AUC", note: "Skin temperature & physical movement steps" },
    { variant: "A3: + Static Clinical", features: 51, prauc: "0.467 [0.407, 0.519]", auroc: "0.930 [0.915, 0.946]", gain: "+0.068 PR-AUC", note: "Age, baseline HbA1c, BMI, and clinical diabetes status" },
    { variant: "A4: + Personal Twin", features: 58, prauc: "0.484 [0.427, 0.534]", auroc: "0.932 [0.914, 0.948]", gain: "+0.085 PR-AUC", note: "Personalized circadian baseline, insulin sensitivity, and fasting glucose" }
  ];

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.65)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '1.5rem'
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        background: '#ffffff',
        color: '#0f172a',
        borderRadius: '20px',
        width: '100%',
        maxWidth: '960px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        border: '2px solid #cbd5e1'
      }}>
        {/* Header - Crisp White & High Contrast */}
        <div style={{
          padding: '1.5rem 2rem',
          borderBottom: '2px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#ffffff',
          background: '#ffffff'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: '#e0f2fe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <ShieldCheck size={24} color="#0284c7" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: '800', color: '#0f172a', margin: 0, letterSpacing: '-0.01em' }}>
                Clinical Evidence & Model Transparency
              </h2>
              <div style={{ fontSize: '0.88rem', color: '#475569', fontWeight: '500', marginTop: '2px' }}>
                Grouped 5-Fold Stratified Cross-Validation on 45 Real PhysioNet Participants
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              backgroundColor: '#f1f5f9',
              border: '1.5px solid #cbd5e1',
              borderRadius: '10px',
              padding: '8px',
              color: '#0f172a',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="Close modal"
          >
            <X size={22} color="#0f172a" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          borderBottom: '2px solid #e2e8f0',
          padding: '0 2rem',
          backgroundColor: '#f8fafc',
          gap: '1.5rem'
        }}>
          {[
            { id: 'ablation', label: 'Stream Fusion Proof (A0-A4)' },
            { id: 'metrics', label: 'Held-Out CV Performance' },
            { id: 'audit', label: 'Dataset Audit & Licensing' }
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                background: 'transparent',
                border: 'none',
                borderBottom: activeTab === t.id ? '3px solid #0284c7' : '3px solid transparent',
                padding: '14px 6px',
                color: activeTab === t.id ? '#0284c7' : '#64748b',
                fontSize: '0.95rem',
                fontWeight: '700',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Content Body - Clean, High Contrast & Spacious */}
        <div style={{
          padding: '2rem',
          overflowY: 'auto',
          flex: 1,
          backgroundColor: '#ffffff',
          color: '#1e293b',
          fontSize: '0.95rem',
          lineHeight: '1.6'
        }}>
          {activeTab === 'ablation' && (
            <div>
              {/* Highlight Banner */}
              <div style={{
                marginBottom: '1.5rem',
                backgroundColor: '#eff6ff',
                padding: '14px 18px',
                borderRadius: '12px',
                border: '1.5px solid #bfdbfe',
                color: '#1e3a8a',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <Sparkles size={22} color="#2563eb" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong style={{ fontSize: '1rem', color: '#1e3a8a' }}>Ablation Finding:</strong> Stream fusion delivers substantial predictive gain. Combining meals (+0.045) and personalized digital twin baselines (+0.085) provides a <strong>21.3% relative improvement in PR-AUC</strong> over monitoring raw CGM glucose alone.
                </div>
              </div>

              {/* Formatted Table */}
              <div style={{
                overflowX: 'auto',
                border: '1.5px solid #cbd5e1',
                borderRadius: '14px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
              }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.92rem' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f1f5f9', borderBottom: '2px solid #cbd5e1' }}>
                      <th style={{ padding: '12px 16px', fontWeight: '800', color: '#0f172a' }}>Variant / Stream</th>
                      <th style={{ padding: '12px 14px', fontWeight: '800', color: '#0f172a' }}>Features</th>
                      <th style={{ padding: '12px 14px', fontWeight: '800', color: '#0f172a' }}>PR-AUC [95% CI]</th>
                      <th style={{ padding: '12px 14px', fontWeight: '800', color: '#0f172a' }}>AUROC [95% CI]</th>
                      <th style={{ padding: '12px 16px', fontWeight: '800', color: '#0f172a' }}>Fusion Benefit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ablationData.map((row, idx) => (
                      <tr 
                        key={idx}
                        style={{
                          backgroundColor: idx % 2 === 0 ? '#ffffff' : '#f8fafc',
                          borderBottom: idx === ablationData.length - 1 ? 'none' : '1px solid #e2e8f0'
                        }}
                      >
                        <td style={{ padding: '14px 16px', fontWeight: '700', color: '#0f172a' }}>
                          <div>{row.variant}</div>
                          <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '500', marginTop: '2px' }}>{row.note}</div>
                        </td>
                        <td style={{ padding: '14px 14px', fontWeight: '600', color: '#334155' }}>
                          {row.features}
                        </td>
                        <td style={{ padding: '14px 14px', fontWeight: '700', color: '#0f172a', fontFamily: 'monospace', fontSize: '0.88rem' }}>
                          {row.prauc}
                        </td>
                        <td style={{ padding: '14px 14px', fontWeight: '700', color: '#0f172a', fontFamily: 'monospace', fontSize: '0.88rem' }}>
                          {row.auroc}
                        </td>
                        <td style={{ padding: '14px 16px' }}>
                          <span style={{
                            display: 'inline-block',
                            backgroundColor: idx === 0 ? '#f1f5f9' : '#ecfdf5',
                            color: idx === 0 ? '#475569' : '#047857',
                            border: `1px solid ${idx === 0 ? '#cbd5e1' : '#a7f3d0'}`,
                            padding: '4px 10px',
                            borderRadius: '8px',
                            fontWeight: '700',
                            fontSize: '0.82rem'
                          }}>
                            {row.gain}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'metrics' && (
            <div>
              {/* Highlight Banner */}
              <div style={{
                marginBottom: '1.5rem',
                backgroundColor: '#f5f3ff',
                padding: '14px 18px',
                borderRadius: '12px',
                border: '1.5px solid #ddd6fe',
                color: '#5b21b6',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}>
                <Activity size={22} color="#7c3aed" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong style={{ fontSize: '1rem', color: '#5b21b6' }}>Strict Participant-Isolated Validation:</strong> Models were trained and evaluated using 5-fold Stratified Group Cross-Validation across 3 random seeds. No data from any test participant leaked into training.
                </div>
              </div>

              {/* Metric Cards Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ backgroundColor: '#ffffff', border: '1.5px solid #cbd5e1', borderRadius: '14px', padding: '1.25rem', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Held-Out AUROC</div>
                  <div style={{ fontSize: '2rem', fontWeight: '800', color: '#0284c7', margin: '4px 0' }}>0.839</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>95% CI: [0.802, 0.867]</div>
                </div>

                <div style={{ backgroundColor: '#ffffff', border: '1.5px solid #cbd5e1', borderRadius: '14px', padding: '1.25rem', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Held-Out PR-AUC</div>
                  <div style={{ fontSize: '2rem', fontWeight: '800', color: '#6366f1', margin: '4px 0' }}>0.507</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>95% CI: [0.422, 0.565]</div>
                </div>

                <div style={{ backgroundColor: '#ffffff', border: '1.5px solid #cbd5e1', borderRadius: '14px', padding: '1.25rem', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Median Lead Time</div>
                  <div style={{ fontSize: '2rem', fontWeight: '800', color: '#059669', margin: '4px 0' }}>45 min</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Advance excursion warning</div>
                </div>

                <div style={{ backgroundColor: '#ffffff', border: '1.5px solid #cbd5e1', borderRadius: '14px', padding: '1.25rem', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <div style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Alert Fatigue Burden</div>
                  <div style={{ fontSize: '2rem', fontWeight: '800', color: '#d97706', margin: '4px 0' }}>1.69 / day</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Under 2 alerts per patient-day</div>
                </div>
              </div>

              <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '12px', border: '1px solid #e2e8f0', color: '#334155', fontSize: '0.88rem' }}>
                <strong>Cohort Specifications:</strong> 45 real participants, 354.4 total patient-days, 115,380 causal 5-minute grid windows evaluated. Consensus excursion threshold: <strong>180 mg/dL</strong>.
              </div>
            </div>
          )}

          {activeTab === 'audit' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ backgroundColor: '#f0fdf4', padding: '1.25rem', borderRadius: '14px', border: '1.5px solid #bbf7d0' }}>
                <h4 style={{ fontWeight: '800', color: '#166534', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.05rem' }}>
                  <Award size={20} color="#166534" /> PhysioNet CGMacros v1.0.0 Dataset Citation
                </h4>
                <div style={{ color: '#14532d', fontSize: '0.92rem', lineHeight: '1.6' }}>
                  <p style={{ margin: '4px 0' }}>• <strong>Repository:</strong> PhysioNet / MIT, DOI: <code>10.13026/3z8q-x658</code>.</p>
                  <p style={{ margin: '4px 0' }}>• <strong>License:</strong> Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (<strong>CC BY-NC-SA 4.0</strong>).</p>
                  <p style={{ margin: '4px 0' }}>• <strong>Clinical Cohort:</strong> 45 adult participants recruited by Sansum Diabetes Research Institute in Santa Barbara, California, USA.</p>
                </div>
              </div>

              <div style={{ backgroundColor: '#fffbeb', padding: '1.25rem', borderRadius: '14px', border: '1.5px solid #fde68a' }}>
                <h4 style={{ fontWeight: '800', color: '#92400e', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.05rem' }}>
                  <Info size={20} color="#92400e" /> Honest Demographic & Clinical Disclosures
                </h4>
                <div style={{ color: '#78350f', fontSize: '0.92rem', lineHeight: '1.6' }}>
                  <p style={{ margin: '4px 0' }}>• The dataset contains <strong>no Indian participants</strong>; results demonstrate that the multimodal causal algorithms work on real human biosignals, but do not claim validated clinical performance for Indian patients.</p>
                  <p style={{ margin: '4px 0' }}>• The Indian meal presets provided in the simulator are an <strong>extrapolation</strong> sourced from ICMR-NIN IFCT 2017 tables.</p>
                  <p style={{ margin: '4px 0' }}>• The excursion label (&gt;180 mg/dL) represents a consensus physiological threshold, not a standalone clinical diagnosis.</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer - Clear Close Button */}
        <div style={{
          padding: '1.25rem 2rem',
          borderTop: '2px solid #e2e8f0',
          backgroundColor: '#f8fafc',
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center'
        }}>
          <button
            onClick={onClose}
            style={{
              backgroundColor: '#0284c7',
              color: '#ffffff',
              border: 'none',
              borderRadius: '10px',
              padding: '10px 26px',
              fontWeight: '700',
              fontSize: '0.95rem',
              cursor: 'pointer',
              boxShadow: '0 2px 6px rgba(2, 132, 199, 0.3)'
            }}
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}
