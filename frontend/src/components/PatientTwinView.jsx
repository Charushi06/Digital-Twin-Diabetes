import React, { useMemo } from 'react';
import { User, Activity, Utensils, Heart, Zap, Clock, Info, AlertTriangle } from 'lucide-react';

export default function PatientTwinView({ 
  patientData, 
  scrubIndex, 
  onScrubChange,
  excursionThreshold = 180.0
}) {
  if (!patientData) {
    return (
      <div className="app-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading Digital Twin data...
      </div>
    );
  }

  const { pid, group, profile, baseline, cohort_stats, timeline, meals, held_out_note } = patientData;
  const currentPoint = timeline[scrubIndex] || timeline[timeline.length - 1] || {};

  // Slice timeline around scrubber for clear, readable chart
  const windowSlice = useMemo(() => {
    const endIdx = Math.min(timeline.length, Math.max(72, scrubIndex + 14));
    const startIdx = Math.max(0, endIdx - 86);
    return timeline.slice(startIdx, endIdx);
  }, [timeline, scrubIndex]);

  const chartHeight = 260;
  const chartWidth = 920;
  const padding = { top: 25, right: 35, bottom: 35, left: 50 };

  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  const gMin = 50;
  const gMax = 280;

  const getY = (val) => {
    if (val === null || val === undefined) return innerHeight;
    const clamped = Math.max(gMin, Math.min(gMax, val));
    return innerHeight - ((clamped - gMin) / (gMax - gMin)) * innerHeight;
  };

  const getX = (idx) => {
    if (windowSlice.length <= 1) return 0;
    return (idx / (windowSlice.length - 1)) * innerWidth;
  };

  const glucosePath = useMemo(() => {
    let p = '';
    windowSlice.forEach((pt, i) => {
      if (pt.glucose !== null) {
        const x = getX(i);
        const y = getY(pt.glucose);
        p += (p === '' ? `M ${x} ${y}` : ` L ${x} ${y}`);
      }
    });
    return p;
  }, [windowSlice]);

  const thresholdY = getY(excursionThreshold);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Top Banner: Twin Parameters & Clinical Profile */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem' }}>
        
        {/* Personal Twin Parameters Card */}
        <div className="app-card" style={{ borderLeft: '5px solid var(--sea-blue)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--text-title)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={20} color="var(--sea-blue)" />
                <span>Learned Personal Twin Profile</span>
              </h3>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                Baseline calibrated over first 48 hours of sensor wear
              </div>
            </div>
            <span className="status-pill pill-green" style={{ fontSize: '0.78rem' }}>
              Calibrated
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: '12px' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: '600' }}>Typical Glucose Level</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--text-title)', marginTop: '2px' }}>
                {baseline?.personal_mean_glucose ? `${baseline.personal_mean_glucose.toFixed(0)} mg/dL` : '—'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Cohort Avg: {cohort_stats.mean_glucose_cohort_median?.toFixed(0)} mg/dL
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: '12px' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: '600' }}>Normal Glucose Variation</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--text-title)', marginTop: '2px' }}>
                {baseline?.personal_sd_glucose ? `±${baseline.personal_sd_glucose.toFixed(1)} mg/dL` : '—'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Cohort Avg: ±{cohort_stats.sd_glucose_cohort_median?.toFixed(1)} mg/dL
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: '12px' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--soothing-amber)', fontWeight: '700' }}>Typical Meal Rise</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--soothing-amber)', marginTop: '2px' }}>
                {baseline?.personal_median_meal_rise ? `+${baseline.personal_median_meal_rise.toFixed(0)} mg/dL` : '—'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Post-meal rise above baseline
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '12px', borderRadius: '12px' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--lavender)', fontWeight: '700' }}>Resting Heart Rate</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--lavender)', marginTop: '2px' }}>
                {baseline?.personal_resting_hr ? `${baseline.personal_resting_hr.toFixed(0)} bpm` : '—'}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Cohort Avg: {cohort_stats.resting_hr_cohort_median?.toFixed(0)} bpm
              </div>
            </div>
          </div>
        </div>

        {/* Static Clinical Profile Card */}
        <div className="app-card" style={{ borderLeft: '5px solid var(--lavender)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--text-title)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <User size={20} color="var(--lavender)" />
                <span>Clinical Laboratory Profile</span>
              </h3>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                Baseline biomarkers from blood test records
              </div>
            </div>
            <span className={`status-pill ${group === 'healthy' ? 'pill-green' : (group === 'prediabetes' ? 'pill-amber' : 'pill-rose')}`}>
              {group === 'type2' ? 'Type 2 Diabetes' : (group.charAt(0).toUpperCase() + group.slice(1))}
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.9rem' }}>
            <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>Age / Sex</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-title)' }}>
                {profile.age}y / {profile.sex_male === 1 ? 'Male' : 'Female'}
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>BMI</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-title)' }}>
                {profile.bmi?.toFixed(1)} kg/m²
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>HbA1c</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '800', color: profile.hba1c > 6.4 ? 'var(--soothing-rose)' : 'var(--soothing-amber)' }}>
                {profile.hba1c?.toFixed(1)}%
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>Fasting Glucose</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-title)' }}>
                {profile.fasting_glucose?.toFixed(0)} mg/dL
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>HOMA-IR (Insulin)</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-title)' }}>
                {profile.homa_ir?.toFixed(2)}
              </div>
            </div>

            <div style={{ background: 'var(--bg-subtle)', padding: '10px 12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>Triglycerides</div>
              <div style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-title)' }}>
                {profile.triglycerides?.toFixed(0)} mg/dL
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Continuous Glucose Monitor Chart */}
      <div className="app-card">
        {/* Chart Header & Scrubber Stats Bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: 'var(--text-title)' }}>
                Continuous Glucose & Meal Timeline
              </h3>
              <span className="status-pill pill-blue" style={{ fontSize: '0.75rem' }}>
                Held-Out Patient Model
              </span>
            </div>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              The red dotted line marks 180 mg/dL (High Glucose Alert threshold).
            </div>
          </div>

          {/* Scrubber Value Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1.25rem',
            background: 'var(--bg-subtle)',
            border: '1px solid var(--border-card)',
            padding: '8px 18px',
            borderRadius: '14px'
          }}>
            <div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>Timeline Time</div>
              <div style={{ fontSize: '0.92rem', fontWeight: '700', color: 'var(--text-title)', fontFamily: 'var(--font-mono)' }}>
                {currentPoint.ts || '—'}
              </div>
            </div>

            <div style={{ borderLeft: '1px solid var(--border-card)', paddingLeft: '1.25rem' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>Glucose Level</div>
              <div style={{ fontSize: '1.15rem', fontWeight: '800', color: currentPoint.glucose > 180 ? 'var(--soothing-rose)' : 'var(--sea-blue)' }}>
                {currentPoint.glucose || '—'} mg/dL
              </div>
            </div>

            <div style={{ borderLeft: '1px solid var(--border-card)', paddingLeft: '1.25rem' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>2-Hour Spike Risk</div>
              <div style={{ fontSize: '1.15rem', fontWeight: '800', color: (currentPoint.risk_120 || 0) > 0.45 ? 'var(--soothing-rose)' : 'var(--soothing-green)' }}>
                {currentPoint.risk_120 !== null ? `${(currentPoint.risk_120 * 100).toFixed(0)}%` : '—'}
              </div>
            </div>
          </div>
        </div>

        {/* Clean, High-Contrast SVG Graph */}
        <div style={{ width: '100%', overflowX: 'auto', background: '#ffffff', borderRadius: '12px', padding: '10px 0' }}>
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ width: '100%', height: 'auto', display: 'block' }}>
            <defs>
              <linearGradient id="softExcursionGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#fee2e2" stopOpacity="0.85" />
                <stop offset="100%" stopColor="#fee2e2" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            <g transform={`translate(${padding.left}, ${padding.top})`}>
              {/* Soft Red Shaded Warning Zone above 180 mg/dL */}
              <rect
                x="0"
                y="0"
                width={innerWidth}
                height={Math.max(0, thresholdY)}
                fill="url(#softExcursionGrad)"
              />

              {/* Clean Reference Lines */}
              {[70, 100, 140, 180, 220, 260].map(val => {
                const y = getY(val);
                return (
                  <g key={val}>
                    <line x1="0" y1={y} x2={innerWidth} y2={y} stroke="#f1f5f9" strokeWidth="1" strokeDasharray={val === excursionThreshold ? '4,4' : 'none'} />
                    <text x="-12" y={y + 4} fill="#64748b" fontSize="11" fontFamily="var(--font-family)" textAnchor="end" fontWeight="500">{val}</text>
                  </g>
                );
              })}

              {/* 180 mg/dL High Glucose Alert Threshold Line */}
              <line x1="0" y1={thresholdY} x2={innerWidth} y2={thresholdY} stroke="#e11d48" strokeWidth="2" strokeDasharray="6,4" />
              <text x={innerWidth - 8} y={thresholdY - 6} fill="#e11d48" fontSize="11" fontFamily="var(--font-family)" textAnchor="end" fontWeight="700">
                ⚠️ 180 mg/dL High Glucose Threshold
              </text>

              {/* Dexcom Glucose Path in Sea Blue */}
              {glucosePath && (
                <path d={glucosePath} fill="none" stroke="#0284c7" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
              )}

              {/* Meal Markers */}
              {windowSlice.map((pt, idx) => {
                const m = meals.find(meal => meal.ts === pt.ts);
                if (!m) return null;
                const x = getX(idx);
                const y = getY(pt.glucose || 120);

                return (
                  <g key={`meal-${idx}`}>
                    <line x1={x} y1={y} x2={x} y2={innerHeight} stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="3,3" />
                    <circle cx={x} cy={y} r="6" fill="#f59e0b" stroke="#ffffff" strokeWidth="2" />
                    <text x={x} y={y - 10} fill="#b45309" fontSize="10" fontFamily="var(--font-family)" textAnchor="middle" fontWeight="700">
                      🍽️ {m.carbs_g}g Carbs
                    </text>
                  </g>
                );
              })}

              {/* Scrubber Position Vertical Line */}
              {(() => {
                const activeSliceIdx = windowSlice.findIndex(pt => pt.t_min === currentPoint.t_min);
                if (activeSliceIdx >= 0) {
                  const x = getX(activeSliceIdx);
                  return (
                    <g>
                      <line x1={x} y1="0" x2={x} y2={innerHeight} stroke="#0284c7" strokeWidth="2" />
                      <circle cx={x} cy={getY(currentPoint.glucose || 120)} r="7" fill="#0284c7" stroke="#ffffff" strokeWidth="2.5" />
                    </g>
                  );
                }
                return null;
              })()}
            </g>
          </svg>
        </div>

        {/* Large, Tactile Timeline Scrubber Slider */}
        <div style={{ marginTop: '1.5rem', background: 'var(--bg-subtle)', padding: '14px 20px', borderRadius: '14px', border: '1px solid var(--border-card)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-title)', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Clock size={16} color="var(--sea-blue)" /> Drag to Scroll Through Days & Hours:
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Step {scrubIndex + 1} of {timeline.length} (5-minute recording intervals)
            </span>
          </div>

          <input
            type="range"
            min="0"
            max={Math.max(0, timeline.length - 1)}
            value={scrubIndex}
            onChange={(e) => onScrubChange(parseInt(e.target.value, 10))}
            style={{ width: '100%' }}
          />
        </div>
      </div>
    </div>
  );
}
