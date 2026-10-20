import React, { useState, useEffect } from 'react';
import { Utensils, AlertTriangle, CheckCircle, Info, Sparkles, Sliders, ArrowRight } from 'lucide-react';

export default function ScenarioSimulator({ 
  pid, 
  currentTMin, 
  onRunScenario, 
  scenarioResult, 
  presetsData,
  isSimulating 
}) {
  const [carbs, setCarbs] = useState(60);
  const [protein, setProtein] = useState(20);
  const [fat, setFat] = useState(15);
  const [fiber, setFiber] = useState(5);
  const [selectedPreset, setSelectedPreset] = useState('');

  const handlePresetChange = (presetName) => {
    setSelectedPreset(presetName);
    const p = presetsData?.presets?.find(item => item.name === presetName);
    if (p) {
      setCarbs(p.carbs_g);
      setProtein(p.protein_g);
      setFat(p.fat_g);
      setFiber(p.fiber_g || 0);
    }
  };

  const handleSimulate = () => {
    onRunScenario({
      t_min: currentTMin,
      carbs_g: carbs,
      protein_g: protein,
      fat_g: fat,
      fiber_g: fiber
    });
  };

  useEffect(() => {
    handleSimulate();
  }, [carbs, protein, fat, fiber, currentTMin]);

  const pBase = scenarioResult?.baseline_prob ?? 0.15;
  const pScen = scenarioResult?.scenario_prob ?? 0.15;
  const delta = scenarioResult?.delta_prob ?? 0.0;

  return (
    <div className="app-card" style={{ height: '100%', borderLeft: '5px solid var(--lavender)' }}>
      {/* Title */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--text-title)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sliders size={20} color="var(--lavender)" />
          <span>Pre-Meal What-If Simulator</span>
        </h3>
        <span className="status-pill pill-lavender" style={{ fontSize: '0.75rem' }}>
          Sensitivity Tool
        </span>
      </div>

      <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1.25rem', lineHeight: '1.5' }}>
        Select a familiar dish or adjust the food nutrient sliders below to test how the patient's glucose spike risk responds <strong>before</strong> the meal is consumed.
      </p>

      {/* Indian Meal Presets Dropdown */}
      {presetsData?.presets?.length > 0 && (
        <div style={{
          marginBottom: '1.5rem',
          background: 'var(--bg-subtle)',
          padding: '14px 16px',
          borderRadius: '14px',
          border: '1px solid var(--border-card)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: '800', color: 'var(--sea-blue-dark)' }}>
              🍛 Pick an Indian Meal Preset:
            </span>
            <span className="status-pill pill-amber" style={{ fontSize: '0.72rem', padding: '2px 8px' }}>
              Extrapolation
            </span>
          </div>

          <select
            value={selectedPreset}
            onChange={(e) => handlePresetChange(e.target.value)}
            style={{
              width: '100%',
              background: '#ffffff',
              color: 'var(--text-title)',
              border: '1px solid var(--border-card)',
              borderRadius: '10px',
              padding: '10px 12px',
              fontSize: '0.92rem',
              fontWeight: '600',
              fontFamily: 'var(--font-family)',
              outline: 'none',
              cursor: 'pointer'
            }}
          >
            <option value="">-- Custom Manual Food Input --</option>
            {presetsData.presets.map((p, idx) => (
              <option key={idx} value={p.name}>
                {p.name} ({p.carbs_g}g Carbs, {p.protein_g}g Protein, {p.fat_g}g Fat)
              </option>
            ))}
          </select>

          {selectedPreset && (
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '8px', lineHeight: '1.4' }}>
              <strong>Scientific Composition Source:</strong> {presetsData.presets.find(p => p.name === selectedPreset)?.source}
            </div>
          )}

          <div style={{ fontSize: '0.75rem', color: 'var(--text-caption)', fontStyle: 'italic', marginTop: '6px' }}>
            "{presetsData.label}"
          </div>
        </div>
      )}

      {/* Nutrient Sliders with large, friendly handles */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem', marginBottom: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', marginBottom: '4px' }}>
            <span style={{ fontWeight: '700', color: 'var(--sea-blue-dark)' }}>Carbohydrates (Sugars & Starches):</span>
            <span style={{ fontWeight: '800', fontSize: '1rem', color: 'var(--text-title)' }}>{carbs} grams</span>
          </div>
          <input
            type="range"
            min="0"
            max="160"
            value={carbs}
            onChange={(e) => { setCarbs(parseFloat(e.target.value)); setSelectedPreset(''); }}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', marginBottom: '4px' }}>
            <span style={{ fontWeight: '700', color: 'var(--lavender-dark)' }}>Protein (Muscle & Satiety):</span>
            <span style={{ fontWeight: '800', fontSize: '1rem', color: 'var(--text-title)' }}>{protein} grams</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={protein}
            onChange={(e) => { setProtein(parseFloat(e.target.value)); setSelectedPreset(''); }}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', marginBottom: '4px' }}>
            <span style={{ fontWeight: '700', color: 'var(--soothing-amber)' }}>Fats:</span>
            <span style={{ fontWeight: '800', fontSize: '1rem', color: 'var(--text-title)' }}>{fat} grams</span>
          </div>
          <input
            type="range"
            min="0"
            max="80"
            value={fat}
            onChange={(e) => { setFat(parseFloat(e.target.value)); setSelectedPreset(''); }}
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.92rem', marginBottom: '4px' }}>
            <span style={{ fontWeight: '700', color: 'var(--soothing-green)' }}>Dietary Fiber (Protective):</span>
            <span style={{ fontWeight: '800', fontSize: '1rem', color: 'var(--text-title)' }}>{fiber} grams</span>
          </div>
          <input
            type="range"
            min="0"
            max="35"
            value={fiber}
            onChange={(e) => { setFiber(parseFloat(e.target.value)); setSelectedPreset(''); }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Side-by-Side Comparison Box */}
      <div style={{
        background: 'var(--bg-subtle)',
        padding: '1.25rem',
        borderRadius: '16px',
        border: '1px solid var(--border-card)',
        marginBottom: '1.25rem'
      }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: '1rem', textAlign: 'center' }}>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>Current Risk</div>
            <div style={{ fontSize: '1.8rem', fontWeight: '800', color: 'var(--text-title)', marginTop: '2px' }}>
              {(pBase * 100).toFixed(0)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>before eating</div>
          </div>

          <div style={{ color: 'var(--text-muted)' }}>
            <ArrowRight size={22} />
          </div>

          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--lavender-dark)', textTransform: 'uppercase', fontWeight: '700' }}>Simulated Risk</div>
            <div style={{ fontSize: '1.8rem', fontWeight: '800', color: pScen > pBase ? 'var(--soothing-rose)' : 'var(--soothing-green)', marginTop: '2px' }}>
              {(pScen * 100).toFixed(0)}%
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: '700', color: delta > 0 ? 'var(--soothing-rose)' : 'var(--soothing-green)' }}>
              {delta > 0 ? `+${(delta * 100).toFixed(1)}% higher` : `${(delta * 100).toFixed(1)}% lower`}
            </div>
          </div>
        </div>

        {/* Monotonicity Guarantee Notice */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '1rem', paddingTop: '0.9rem', borderTop: '1px solid var(--border-card)', fontSize: '0.78rem', color: 'var(--soothing-green)' }}>
          <CheckCircle size={15} />
          <span><strong>Monotonic Guarantee:</strong> Adding carbohydrates will never artificially lower predicted risk.</span>
        </div>
      </div>

      {/* Out of Distribution Warnings */}
      {scenarioResult?.ood_warnings?.length > 0 && (
        <div style={{
          background: 'var(--soothing-amber-light)',
          border: '1px solid #fde68a',
          borderRadius: '12px',
          padding: '10px 14px',
          marginBottom: '1rem',
          fontSize: '0.82rem',
          color: '#92400e'
        }}>
          <div style={{ fontWeight: '700', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px' }}>
            <AlertTriangle size={15} /> High Food Quantity Alert:
          </div>
          {scenarioResult.ood_warnings.map((w, i) => (
            <div key={i} style={{ marginLeft: '18px' }}>• {w}</div>
          ))}
        </div>
      )}

      {/* Mandatory Regulatory Disclaimer */}
      <div style={{
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
        lineHeight: '1.45',
        borderTop: '1px solid var(--border-card)',
        paddingTop: '0.9rem'
      }}>
        <strong>Clinical Advisory Notice:</strong> {scenarioResult?.disclaimer || "Sensitivity analysis on model inputs. Not a treatment simulation, not proof of causation, not medical advice."}
      </div>
    </div>
  );
}
