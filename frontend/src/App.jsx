/**
 * WildLink AI — Main App Component
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ConservationMap from './components/Map/ConservationMap';
import ZoneDetailModal from './components/ZoneDetailModal';
import SimulationPanel from './components/SimulationPanel';
import {
  getSpecies, getProjects, getProject, createProject, getDashboard,
  runAnalysis, getJobStatus, getHabitatZones, getCorridors,
  getPriorityZones, getObservations
} from './services/api';
import './App.css';

// ──────────── Toast System ────────────
function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="toast-container">
      {toasts.map(t => (
        <div key={t.id} className={`toast toast-${t.type}${t.exiting ? ' exit' : ''}`}>
          <span style={{ flex: 1 }}>{t.message}</span>
          <button
            onClick={() => onRemove(t.id)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'currentColor', padding: '0 0 0 8px', opacity: 0.7, lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}

function useToast() {
  const [toasts, setToasts] = useState([]);
  const counterRef = useRef(0);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++counterRef.current;
    setToasts(prev => [...prev, { id, message, type, exiting: false }]);
    if (duration > 0) {
      setTimeout(() => {
        // Start exit animation
        setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t));
        setTimeout(() => {
          setToasts(prev => prev.filter(t => t.id !== id));
        }, 300);
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t));
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300);
  }, []);

  return { toasts, addToast, removeToast };
}

// ──────────── App ────────────
function App() {
  const { toasts, addToast, removeToast } = useToast();

  // State
  const [species, setSpecies] = useState([]);
  const [selectedSpecies, setSelectedSpecies] = useState(null);
  const [project, setProject] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');

  // Map layers
  const [layers, setLayers] = useState({
    observations: { visible: true, data: null, color: '#f59e0b' },
    habitat: { visible: true, data: null, color: '#22c55e' },
    corridors: { visible: true, data: null, color: '#3b82f6' },
    priority: { visible: true, data: null, color: '#ef4444' },
  });

  // Analysis state
  const [analysisStatus, setAnalysisStatus] = useState('idle');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [selectedZone, setSelectedZone] = useState(null);
  const [showSimulation, setShowSimulation] = useState(false);

  // Priority zones
  const [priorityZones, setPriorityZones] = useState([]);

  // ────────── Load initial data ──────────
  useEffect(() => {
    loadSpecies();
    checkUrlHash();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const checkUrlHash = async () => {
    const hash = window.location.hash.replace('#', '');
    if (hash) {
      try {
        const res = await getProject(hash);
        if (res.data.data) {
          const proj = res.data.data;
          setProject(proj);
          if (proj.species) {
            setSelectedSpecies(proj.species);
          }
          const dashRes = await getDashboard(proj.id);
          setDashboard(dashRes.data.data);
          setAnalysisStatus('completed');
          await loadAnalysisResultsForProject(proj.id);
          addToast(`Restored project: ${proj.name}`, 'success');
        }
      } catch (e) {
        console.warn('Could not load project from hash:', e);
        window.location.hash = '';
      }
    }
  };

  const loadSpecies = async () => {
    try {
      const res = await getSpecies();
      setSpecies(res.data.data || []);
    } catch (err) {
      console.error('Failed to load species:', err);
      addToast('Failed to load species list. Is the backend running?', 'error', 6000);
    }
  };

  // ────────── Project Creation ──────────
  const handleCreateProject = async (speciesId) => {
    try {
      const sp = species.find(s => s.id === speciesId);
      setSelectedSpecies(sp);

      addToast('Setting up project...', 'info', 2000);

      // Check if project already exists for this species
      const existingProjectsRes = await getProjects();
      const existing = (existingProjectsRes.data.data || []).find(p => p.species_id === speciesId);

      let proj = null;
      if (existing) {
        proj = existing;
        addToast(`Loaded existing project for ${sp?.common_name}`, 'success');
      } else {
        const res = await createProject({
          name: `${sp?.common_name || 'Wildlife'} Corridor Analysis`,
          description: `Habitat connectivity analysis for ${sp?.common_name || 'target species'} in Central Indian Highlands`,
          region_name: 'Central Indian Highlands',
          species_id: speciesId,
        });
        proj = res.data.data;
        addToast(`Project created for ${sp?.common_name}`, 'success');
      }

      setProject(proj);
      window.location.hash = proj.id;

      // Load dashboard
      const dashRes = await getDashboard(proj.id);
      setDashboard(dashRes.data.data);

      // Check if analysis is already completed for this project
      if (proj.status === 'completed' || dashRes.data.data?.total_corridors > 0) {
        setAnalysisStatus('completed');
        await loadAnalysisResultsForProject(proj.id);
        addToast('Previous analysis results loaded', 'info');
      } else {
        setAnalysisStatus('idle');
      }
    } catch (err) {
      console.error('Failed to set up project:', err);
      addToast('Failed to create project. Please try again.', 'error');
      throw err; // Re-throw so Sidebar can clear loading state
    }
  };

  // ────────── Run Analysis ──────────
  const handleRunAnalysis = async () => {
    if (!project) return;

    setAnalysisStatus('running');
    setAnalysisProgress(0);

    // Clear old layer data
    setLayers(prev => ({
      observations: { ...prev.observations, data: null },
      habitat: { ...prev.habitat, data: null },
      corridors: { ...prev.corridors, data: null },
      priority: { ...prev.priority, data: null },
    }));
    setPriorityZones([]);

    addToast('Analysis pipeline started...', 'info', 3000);

    try {
      const res = await runAnalysis({
        project_id: project.id,
        type: 'full',
      });

      const jobId = res.data.data?.id;
      if (jobId) {
        pollJobStatus(jobId);
      } else {
        throw new Error('No job ID returned');
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      setAnalysisStatus('failed');
      addToast('Failed to start analysis. Please try again.', 'error');
    }
  };

  const pollJobStatus = (jobId) => {
    let consecutiveErrors = 0;
    const poll = setInterval(async () => {
      try {
        const res = await getJobStatus(jobId);
        const job = res.data.data;
        consecutiveErrors = 0;

        setAnalysisProgress(job.progress || 0);

        if (job.status === 'completed') {
          clearInterval(poll);
          setAnalysisStatus('completed');
          addToast('Analysis complete! Loading results...', 'success');
          await loadAnalysisResults();
        } else if (job.status === 'failed') {
          clearInterval(poll);
          setAnalysisStatus('failed');
          addToast(`Analysis failed: ${job.error || 'Unknown error'}`, 'error', 6000);
        }
      } catch (err) {
        consecutiveErrors++;
        console.warn(`Polling error count ${consecutiveErrors}:`, err);
        if (consecutiveErrors > 15) {
          clearInterval(poll);
          setAnalysisStatus('failed');
          addToast('Lost connection to backend. Analysis may still be running.', 'error', 6000);
        }
      }
    }, 2000);
  };

  // ────────── Load Results ──────────
  const loadAnalysisResultsForProject = async (projId) => {
    try {
      const [habitatRes, corridorRes, priorityRes, obsRes, dashRes] = await Promise.all([
        getHabitatZones(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getCorridors(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getPriorityZones(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getObservations(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getDashboard(projId),
      ]);

      setLayers(prev => ({
        ...prev,
        habitat: { ...prev.habitat, data: habitatRes.data.data },
        corridors: { ...prev.corridors, data: corridorRes.data.data },
        priority: { ...prev.priority, data: priorityRes.data.data },
        observations: { ...prev.observations, data: obsRes.data.data },
      }));

      const pzFeatures = priorityRes.data.data?.features || [];
      setPriorityZones(pzFeatures.map(f => ({ ...f.properties, geometry: f.geometry })));

      setDashboard(dashRes.data.data);
    } catch (err) {
      console.error('Failed to load results:', err);
      addToast('Some results failed to load.', 'warning');
    }
  };

  const loadAnalysisResults = async () => {
    if (!project) return;
    await loadAnalysisResultsForProject(project.id);
  };

  // ────────── Layer Toggle ──────────
  const toggleLayer = (layerName) => {
    setLayers(prev => ({
      ...prev,
      [layerName]: { ...prev[layerName], visible: !prev[layerName].visible },
    }));
  };

  // ────────── Zone Selection ──────────
  const handleZoneClick = (zone) => {
    setSelectedZone(zone);
  };

  return (
    <div className="app-layout">
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100vh' }}>
        <Header
          project={project}
          species={selectedSpecies}
          analysisStatus={analysisStatus}
        />

        <div className="app-main">
          <Sidebar
            species={species}
            selectedSpecies={selectedSpecies}
            project={project}
            dashboard={dashboard}
            layers={layers}
            activeTab={activeTab}
            analysisStatus={analysisStatus}
            analysisProgress={analysisProgress}
            priorityZones={priorityZones}
            onSelectSpecies={handleCreateProject}
            onToggleLayer={toggleLayer}
            onRunAnalysis={handleRunAnalysis}
            onTabChange={setActiveTab}
            onZoneClick={handleZoneClick}
            onOpenSimulation={() => setShowSimulation(true)}
          />

          <div className="map-container">
            <ConservationMap
              layers={layers}
              onZoneClick={handleZoneClick}
            />
          </div>
        </div>
      </div>

      {selectedZone && (
        <ZoneDetailModal
          zone={selectedZone}
          onClose={() => setSelectedZone(null)}
          onSimulate={() => {
            setShowSimulation(true);
            setSelectedZone(null);
          }}
        />
      )}

      {showSimulation && project && (
        <SimulationPanel
          project={project}
          priorityZones={priorityZones}
          onClose={() => setShowSimulation(false)}
        />
      )}

      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}

export default App;
