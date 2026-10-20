import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import PanelView from './components/PanelView';
import PatientTwinView from './components/PatientTwinView';
import DriversPanel from './components/DriversPanel';
import ScenarioSimulator from './components/ScenarioSimulator';
import ModelTransparencyModal from './components/ModelTransparencyModal';
import GuidedTour from './components/GuidedTour';
import { AlertTriangle, ShieldCheck, HeartPulse, Info, HelpCircle } from 'lucide-react';

const API_BASE = '/api';

export default function App() {
  const [patients, setPatients] = useState([]);
  const [selectedPid, setSelectedPid] = useState('');
  const [patientData, setPatientData] = useState(null);
  const [scrubIndex, setScrubIndex] = useState(0);
  
  // Replay state
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const replayIntervalRef = useRef(null);

  // Drivers and Scenario state
  const [drivers, setDrivers] = useState([]);
  const [isDriversLoading, setIsDriversLoading] = useState(false);
  const [scenarioResult, setScenarioResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [presetsData, setPresetsData] = useState(null);

  // Transparency Modal & Tour state
  const [isTransparencyOpen, setIsTransparencyOpen] = useState(false);
  const [activeView, setActiveView] = useState('twin'); // 'twin' | 'panel'
  const [isTourOpen, setIsTourOpen] = useState(false);
  const [tourStep, setTourStep] = useState(0);

  // Open tour on first visit
  useEffect(() => {
    const hasSeen = localStorage.getItem('gluco_tour_seen');
    if (!hasSeen) {
      setIsTourOpen(true);
    }
  }, []);

  // Fetch panel patient list
  useEffect(() => {
    fetch(`${API_BASE}/patients`)
      .then(res => res.json())
      .then(data => {
        if (data.patients && data.patients.length > 0) {
          setPatients(data.patients);
          setSelectedPid(data.patients[0].pid);
        }
      })
      .catch(err => console.error("Error fetching patients:", err));

    fetch(`${API_BASE}/presets`)
      .then(res => res.json())
      .then(data => setPresetsData(data))
      .catch(err => console.error("Error fetching presets:", err));
  }, []);

  // Fetch individual patient digital twin data
  useEffect(() => {
    if (!selectedPid) return;
    fetch(`${API_BASE}/patients/${selectedPid}`)
      .then(res => res.json())
      .then(data => {
        setPatientData(data);
        // Default scrubber to the end of the timeline
        setScrubIndex(Math.max(0, data.timeline.length - 1));
      })
      .catch(err => console.error("Error fetching patient detail:", err));
  }, [selectedPid]);

  // Fetch drivers when scrubIndex or patient changes
  useEffect(() => {
    if (!selectedPid || !patientData?.timeline?.[scrubIndex]) return;
    const pt = patientData.timeline[scrubIndex];
    setIsDriversLoading(true);

    fetch(`${API_BASE}/patients/${selectedPid}/drivers?t_min=${pt.t_min}`)
      .then(res => res.json())
      .then(data => {
        setDrivers(data.drivers || []);
        setIsDriversLoading(false);
      })
      .catch(err => {
        console.error("Error fetching drivers:", err);
        setIsDriversLoading(false);
      });
  }, [selectedPid, scrubIndex, patientData]);

  // Replay playback ticker
  useEffect(() => {
    if (isPlaying && patientData?.timeline?.length) {
      const intervalMs = Math.max(50, Math.floor(1000 / playbackSpeed));
      replayIntervalRef.current = setInterval(() => {
        setScrubIndex(prev => {
          if (prev >= patientData.timeline.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, intervalMs);
    } else {
      if (replayIntervalRef.current) clearInterval(replayIntervalRef.current);
    }
    return () => {
      if (replayIntervalRef.current) clearInterval(replayIntervalRef.current);
    };
  }, [isPlaying, playbackSpeed, patientData]);

  // Run What-If Scenario simulation
  const handleRunScenario = (params) => {
    if (!selectedPid) return;
    setIsSimulating(true);
    fetch(`${API_BASE}/patients/${selectedPid}/scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    })
      .then(res => res.json())
      .then(data => {
        setScenarioResult(data);
        setIsSimulating(false);
      })
      .catch(err => {
        console.error("Error running scenario:", err);
        setIsSimulating(false);
      });
  };

  const currentTMin = patientData?.timeline?.[scrubIndex]?.t_min || 0;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-app)' }}>
      {/* Top Header with Replay & Tour trigger */}
      <Header
        patients={patients}
        selectedPid={selectedPid}
        onSelectPid={setSelectedPid}
        isPlaying={isPlaying}
        onTogglePlay={() => setIsPlaying(!isPlaying)}
        playbackSpeed={playbackSpeed}
        onChangeSpeed={setPlaybackSpeed}
        currentTs={patientData?.timeline?.[scrubIndex]?.ts}
        onOpenTransparency={() => setIsTransparencyOpen(true)}
        onStartTour={() => {
          setTourStep(0);
          setIsTourOpen(true);
        }}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '1.5rem 2rem', maxWidth: '1600px', margin: '0 auto', width: '100%' }}>
        
        {/* Navigation Tabs between Panel & Selected Twin */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={() => setActiveView('twin')}
              style={{
                background: activeView === 'twin' ? 'var(--sea-blue)' : '#ffffff',
                color: activeView === 'twin' ? '#ffffff' : 'var(--text-body)',
                border: `1px solid ${activeView === 'twin' ? 'var(--sea-blue)' : 'var(--border-card)'}`,
                borderRadius: '12px',
                padding: '10px 22px',
                fontWeight: '700',
                fontSize: '0.95rem',
                boxShadow: activeView === 'twin' ? '0 4px 12px rgba(2, 132, 199, 0.25)' : 'var(--shadow-sm)',
                transition: 'all 0.2s ease',
                cursor: 'pointer'
              }}
            >
              Patient Digital Twin ({selectedPid || 'Loading...'})
            </button>

            <button
              onClick={() => setActiveView('panel')}
              style={{
                background: activeView === 'panel' ? 'var(--sea-blue)' : '#ffffff',
                color: activeView === 'panel' ? '#ffffff' : 'var(--text-body)',
                border: `1px solid ${activeView === 'panel' ? 'var(--sea-blue)' : 'var(--border-card)'}`,
                borderRadius: '12px',
                padding: '10px 22px',
                fontWeight: '700',
                fontSize: '0.95rem',
                boxShadow: activeView === 'panel' ? '0 4px 12px rgba(2, 132, 199, 0.25)' : 'var(--shadow-sm)',
                transition: 'all 0.2s ease',
                cursor: 'pointer'
              }}
            >
              All Monitored Patients ({patients.length})
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="status-pill pill-green" style={{ fontSize: '0.82rem' }}>
              <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#059669', marginRight: '6px' }} />
              PhysioNet CGMacros Real Streams
            </span>

            <button
              onClick={() => {
                setTourStep(0);
                setIsTourOpen(true);
              }}
              style={{
                background: '#ffffff',
                border: '1px solid var(--border-card)',
                color: 'var(--sea-blue)',
                borderRadius: '10px',
                padding: '7px 14px',
                fontSize: '0.85rem',
                fontWeight: '700',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: 'var(--shadow-sm)',
                cursor: 'pointer'
              }}
            >
              <HelpCircle size={16} /> Need help? Tour guide
            </button>
          </div>
        </div>

        {/* Panel View Tab */}
        {activeView === 'panel' && (
          <PanelView
            patients={patients}
            selectedPid={selectedPid}
            onSelectPatient={(pid) => {
              setSelectedPid(pid);
              setActiveView('twin');
            }}
          />
        )}

        {/* Digital Twin Interactive View Tab */}
        {activeView === 'twin' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Top row: Interactive Multi-Stream Horizon & Digital Twin Parameters */}
            <PatientTwinView
              patientData={patientData}
              scrubIndex={scrubIndex}
              onScrubChange={setScrubIndex}
              excursionThreshold={patientData?.excursion_threshold || 180.0}
            />

            {/* Bottom row: Explainability Drivers + Pre-Meal Sensitivity Simulator */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(440px, 1fr))', gap: '1.5rem' }}>
              <DriversPanel
                drivers={drivers}
                isLoading={isDriversLoading}
              />

              <ScenarioSimulator
                pid={selectedPid}
                currentTMin={currentTMin}
                onRunScenario={handleRunScenario}
                scenarioResult={scenarioResult}
                presetsData={presetsData}
                isSimulating={isSimulating}
              />
            </div>
          </div>
        )}
      </main>

      {/* Mandatory Disclaimer Footer (PRD 10.4 & 17) */}
      <footer style={{
        borderTop: '1px solid var(--border-card)',
        background: '#ffffff',
        padding: '1.25rem 2rem',
        fontSize: '0.85rem',
        color: 'var(--text-muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1.25rem',
        boxShadow: '0 -2px 10px rgba(15, 23, 42, 0.03)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'var(--soothing-amber-light)',
            padding: '6px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <AlertTriangle size={18} color="var(--soothing-amber)" />
          </div>
          <span style={{ color: 'var(--text-body)' }}>
            <strong>Clinical Safety Notice:</strong> Advisory forecast from a research prototype. Not a diagnosis, treatment simulation, or medical advice.
          </span>
        </div>

        <div style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>
          Replay of recorded data (CGMacros v1.0.0, PhysioNet CC BY-NC-SA 4.0). Not a live patient.
        </div>
      </footer>

      {/* Model Transparency & Ablation Modal */}
      <ModelTransparencyModal
        isOpen={isTransparencyOpen}
        onClose={() => setIsTransparencyOpen(false)}
      />

      {/* Interactive Step-by-Step Guided Tour */}
      <GuidedTour
        isOpen={isTourOpen}
        currentStep={tourStep}
        onNext={() => setTourStep(prev => prev + 1)}
        onPrev={() => setTourStep(prev => Math.max(0, prev - 1))}
        onSkip={() => {
          setIsTourOpen(false);
          localStorage.setItem('gluco_tour_seen', 'true');
        }}
      />
    </div>
  );
}
