import React from 'react';
import { HelpCircle, ChevronRight, ChevronLeft, X, Sparkles, Activity, Utensils, Sliders, ShieldCheck } from 'lucide-react';

export default function GuidedTour({ currentStep, onNext, onPrev, onSkip, isOpen }) {
  if (!isOpen) return null;

  const tourSteps = [
    {
      title: "Welcome to GlucoTwin! 👋",
      subtitle: "Your Digital Health Assistant",
      icon: <Sparkles size={28} color="#0284c7" />,
      content: (
        <div>
          <p style={{ marginBottom: '10px' }}>
            This application creates a <strong>virtual digital twin</strong> of a person to predict how their blood glucose responds to daily meals and activities.
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            Designed for doctors, dietitians, and patients to easily see <strong>risk warnings up to 2 hours in advance</strong> before high blood sugar occurs.
          </p>
        </div>
      )
    },
    {
      title: "1. The Patient Panel View 👥",
      subtitle: "Monitor All Patients at a Glance",
      icon: <Activity size={28} color="#6366f1" />,
      content: (
        <div>
          <p style={{ marginBottom: '10px' }}>
            Click the <strong>'All Monitored Patients'</strong> tab above to view a list of all patients sorted by their 2-hour glucose spike risk.
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            Patients needing the most attention appear at the very top with clear badges like <em>'High Now'</em> or <em>'Twin Ready'</em>.
          </p>
        </div>
      )
    },
    {
      title: "2. The Continuous Glucose Trace 📈",
      subtitle: "Live Trend & The 180 mg/dL Safety Threshold",
      icon: <Activity size={28} color="#059669" />,
      content: (
        <div>
          <p style={{ marginBottom: '10px' }}>
            The main graph shows the patient's continuous glucose monitor (CGM) line.
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            The red dotted line marks <strong>180 mg/dL</strong> (the medical threshold for high glucose). When the line rises above it, the area is shaded in soft red.
            Small 🍽️ fork icons indicate when the person ate a meal.
          </p>
        </div>
      )
    },
    {
      title: "3. Understand 'Why' with AI Drivers 💡",
      subtitle: "Clear, Plain-Language Explanations",
      icon: <HelpCircle size={28} color="#0284c7" />,
      content: (
        <div>
          <p style={{ marginBottom: '10px' }}>
            Instead of confusing formulas, the AI explains risk in plain sentences:
          </p>
          <p style={{ background: 'var(--bg-highlight)', padding: '10px 14px', borderRadius: '10px', fontSize: '0.88rem', fontStyle: 'italic', marginBottom: '10px' }}>
            "Risk is elevated because the last meal contained 85g of carbohydrates and glucose has risen +38 mg/dL in the last 30 minutes."
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            Green arrows mean helpful factors; red arrows point out what is raising the risk.
          </p>
        </div>
      )
    },
    {
      title: "4. Pre-Meal What-If Simulator 🍽️",
      subtitle: "Test Meal Changes Before Eating",
      icon: <Sliders size={28} color="#d97706" />,
      content: (
        <div>
          <p style={{ marginBottom: '10px' }}>
            Curious how a meal will impact glucose? Drag the sliders for <strong>Carbohydrates, Protein, and Fiber</strong>, or pick a familiar Indian dish from the dropdown (like <em>Idli, Dosa, or Roti-Dal</em>).
          </p>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem' }}>
            The twin will immediately show the difference: <strong>Baseline Risk vs. Scenario Risk</strong> so you can plan healthier food choices in advance.
          </p>
        </div>
      )
    }
  ];

  const step = tourSteps[currentStep] || tourSteps[0];
  const isLast = currentStep === tourSteps.length - 1;

  return (
    <div className="tour-overlay">
      <div className="tour-card">
        {/* Header with step number & close */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'var(--bg-highlight)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {step.icon}
            </div>
            <div>
              <span style={{ fontSize: '0.78rem', color: 'var(--sea-blue)', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Step {currentStep + 1} of {tourSteps.length}
              </span>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: 'var(--text-title)' }}>
                {step.title}
              </h3>
            </div>
          </div>

          <button
            onClick={onSkip}
            style={{
              background: 'var(--bg-subtle)',
              border: '1px solid var(--border-card)',
              color: 'var(--text-muted)',
              padding: '6px',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Close Guide"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ fontSize: '1rem', color: 'var(--text-body)', lineHeight: '1.6', marginBottom: '1.75rem' }}>
          {step.content}
        </div>

        {/* Progress dots & action buttons */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
          {/* Dots */}
          <div style={{ display: 'flex', gap: '6px' }}>
            {tourSteps.map((_, idx) => (
              <div
                key={idx}
                style={{
                  width: idx === currentStep ? '20px' : '8px',
                  height: '8px',
                  borderRadius: '4px',
                  background: idx === currentStep ? 'var(--sea-blue)' : '#cbd5e1',
                  transition: 'all 0.25s ease'
                }}
              />
            ))}
          </div>

          {/* Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {currentStep > 0 && (
              <button
                onClick={onPrev}
                style={{
                  background: 'var(--bg-subtle)',
                  color: 'var(--text-body)',
                  border: '1px solid var(--border-card)',
                  padding: '9px 16px',
                  fontSize: '0.9rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <ChevronLeft size={16} /> Back
              </button>
            )}

            <button
              onClick={isLast ? onSkip : onNext}
              style={{
                background: 'var(--sea-blue)',
                color: '#ffffff',
                border: 'none',
                padding: '9px 20px',
                fontSize: '0.92rem',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 4px 12px rgba(2, 132, 199, 0.25)'
              }}
            >
              {isLast ? "Got it! Start Exploring" : "Next"} {!isLast && <ChevronRight size={16} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
