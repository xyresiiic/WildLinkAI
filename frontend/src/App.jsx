/**
 * WildLink AI — Main App Component
 */
import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ConservationMap from './components/Map/ConservationMap';
import ZoneDetailModal from './components/ZoneDetailModal';
import SimulationPanel from './components/SimulationPanel';
import {
  getSpecies,
  getProjects,
  getProject,
  createProject,
  getDashboard,
  runAnalysis,
  getJobStatus,
  getHabitatZones,
  getCorridors,
  getPriorityZones,
  getObservations,
  exportProjectData,
} from './services/api';
import './App.css';

// ──────────── Toast System ────────────
let toastIdCounter = 0;

function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`toast toast-${toast.type} animate-fade-in`}
          onClick={() => onRemove(toast.id)}
          role="alert"
        >
          <span style={{ fontSize: '1.1rem' }}>
            {toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : toast.type === 'warning' ? '⚠️' : 'ℹ️'}
          </span>
          <span style={{ fontSize: '0.85rem' }}>{toast.message}</span>
        </div>
      ))}
    </div>
  );
}

function useToast() {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const addToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = ++toastIdCounter;
    setToasts(prev => [...prev, { id, message, type }]);
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration);
    }
  }, [removeToast]);

  return { toasts, addToast, removeToast };
}

// ──────────── App ────────────
function App() {
  const { toasts, addToast, removeToast } = useToast();

  // State
  const [species, setSpecies] = useState([]);
  const [projectsList, setProjectsList] = useState([]);
  const [selectedSpecies, setSelectedSpecies] = useState(null);
  const [project, setProject] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');
  const [focusCoords, setFocusCoords] = useState(null);

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
    loadProjects();
    checkUrlHash();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadProjects = async () => {
    try {
      const res = await getProjects();
      setProjectsList(res.data.data || []);
    } catch (err) {
      console.warn('Failed to load projects list:', err);
    }
  };

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
      addToast('Failed to load species catalogue. Ensure backend is running.', 'error', 6000);
    }
  };

  // ────────── Project Switcher ──────────
  const handleSelectProject = async (projectId) => {
    try {
      addToast('Loading project...', 'info', 1500);
      const res = await getProject(projectId);
      const proj = res.data.data;
      setProject(proj);
      if (proj.species) setSelectedSpecies(proj.species);
      window.location.hash = proj.id;

      const dashRes = await getDashboard(proj.id).catch(() => ({ data: { data: null } }));
      setDashboard(dashRes.data.data);

      // Always load observations for the species
      const obsRes = await getObservations(proj.id).catch(() => ({ data: { data: { count: 0, features: [] } } }));

      if (proj.status === 'completed' || dashRes.data.data?.total_corridors > 0) {
        setAnalysisStatus('completed');
        await loadAnalysisResultsForProject(proj.id);
      } else {
        setAnalysisStatus('idle');
        setLayers(prev => ({
          observations: { ...prev.observations, data: obsRes.data.data },
          habitat: { ...prev.habitat, data: null },
          corridors: { ...prev.corridors, data: null },
          priority: { ...prev.priority, data: null },
        }));
        setPriorityZones([]);
      }
      addToast(`Switched to: ${proj.name}`, 'success');
    } catch (err) {
      console.error('Failed to switch project:', err);
      addToast('Failed to switch project.', 'error');
    }
  };

  const handleNewAnalysis = () => {
    setProject(null);
    setSelectedSpecies(null);
    setDashboard(null);
    setAnalysisStatus('idle');
    setPriorityZones([]);
    setFocusCoords(null);
    setLayers(prev => ({
      observations: { ...prev.observations, data: null },
      habitat: { ...prev.habitat, data: null },
      corridors: { ...prev.corridors, data: null },
      priority: { ...prev.priority, data: null },
    }));
    window.location.hash = '';
    loadProjects();
    addToast('Select a species to configure a new analysis.', 'info');
  };

  // ────────── Export GeoJSON Bundle ──────────
  const handleExportData = async () => {
    if (!project) return;
    try {
      addToast('Preparing conservation export bundle...', 'info', 2000);
      const res = await exportProjectData(project.id);
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(res.data.data, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', `${project.name.toLowerCase().replace(/\s+/g, '_')}_conservation_bundle.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      addToast('Conservation report & GeoJSON downloaded successfully!', 'success');
    } catch (err) {
      console.error('Export failed:', err);
      addToast('Failed to export conservation report.', 'error');
    }
  };

  // ────────── Project Creation ──────────
  const handleCreateProject = async (speciesId) => {
    try {
      const sp = species.find(s => s.id === speciesId);
      setSelectedSpecies(sp);

      addToast('Setting up conservation project...', 'info', 2000);

      // Check if project already exists for this species
      const existingProjectsRes = await getProjects();
      const existingList = existingProjectsRes.data.data || [];
      setProjectsList(existingList);
      const existing = existingList.find(p => p.species_id === speciesId);

      const SPECIES_REGIONS = {
        'Bengal Tiger': 'Central Indian Highlands (Kanha–Bandhavgarh–Pench)',
        'Snow Leopard': 'Western Himalayas (Ladakh & Spiti Valley)',
        'Gharial': 'National Chambal River Sanctuary',
        'Great Indian Bustard': 'Thar Desert & Semi-Arid Grasslands (Jaisalmer)',
        'Indian Elephant': 'Western Ghats & Nilgiri Biosphere',
        'Indian Leopard': 'Satpura & Aravalli Rocky Landscape',
        'Sloth Bear': 'Daroji Sloth Bear Sanctuary & Deccan Plateau',
      };

      let proj = null;
      if (existing) {
        proj = existing;
        addToast(`Loaded project for ${sp?.common_name}`, 'success');
      } else {
        const regionName = SPECIES_REGIONS[sp?.common_name] || 'Regional Wildlife Corridor';
        const res = await createProject({
          name: `${sp?.common_name || 'Wildlife'} Corridor Analysis`,
          description: `Habitat connectivity and least-cost corridor analysis for ${sp?.common_name || 'target species'} across ${regionName}.`,
          region_name: regionName,
          species_id: speciesId,
        });
        proj = res.data.data;
        addToast(`Created project for ${sp?.common_name}`, 'success');
        loadProjects();
      }

      setProject(proj);
      window.location.hash = proj.id;

      // Load dashboard
      const dashRes = await getDashboard(proj.id).catch(() => ({ data: { data: null } }));
      setDashboard(dashRes.data.data);

      // Always load observations immediately for visual context
      const obsRes = await getObservations(proj.id).catch(() => ({ data: { data: { count: 0, features: [] } } }));

      if (proj.status === 'completed' || dashRes.data.data?.total_corridors > 0) {
        setAnalysisStatus('completed');
        await loadAnalysisResultsForProject(proj.id);
      } else {
        setAnalysisStatus('idle');
        setLayers(prev => ({
          observations: { ...prev.observations, data: obsRes.data.data },
          habitat: { ...prev.habitat, data: null },
          corridors: { ...prev.corridors, data: null },
          priority: { ...prev.priority, data: null },
        }));
        setPriorityZones([]);
      }
    } catch (err) {
      console.error('Failed to set up project:', err);
      addToast('Failed to create project. Please try again.', 'error');
      throw err;
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

    addToast('Executing ecological analysis pipeline...', 'info', 3000);

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
      addToast('Failed to start analysis pipeline.', 'error');
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
          addToast('Analysis complete! Rendering results...', 'success');
          await loadAnalysisResults();
          loadProjects();
        } else if (job.status === 'failed') {
          clearInterval(poll);
          setAnalysisStatus('failed');
          addToast(`Analysis failed: ${job.error || 'Unknown error'}`, 'error', 6000);
        }
      } catch (err) {
        consecutiveErrors++;
        if (consecutiveErrors > 15) {
          clearInterval(poll);
          setAnalysisStatus('failed');
          addToast('Lost connection to backend.', 'error', 6000);
        }
      }
    }, 1800);
  };

  // ────────── Load Results ──────────
  const loadAnalysisResultsForProject = async (projId) => {
    try {
      const [habitatRes, corridorRes, priorityRes, obsRes, dashRes] = await Promise.all([
        getHabitatZones(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getCorridors(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getPriorityZones(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getObservations(projId).catch(() => ({ data: { data: { count: 0, features: [] } } })),
        getDashboard(projId).catch(() => ({ data: { data: null } })),
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
      addToast('Some layer datasets could not be loaded.', 'warning');
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

  // ────────── Global Keyboard Shortcuts ──────────
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't trigger if user is typing in an input or textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;

      if (e.key === 'Escape') {
        if (selectedZone) setSelectedZone(null);
        if (showSimulation) setShowSimulation(false);
      } else if ((e.key === 's' || e.key === 'S') && project) {
        setShowSimulation(prev => !prev);
      } else if ((e.key === 'e' || e.key === 'E') && project) {
        handleExportData();
      } else if (e.key === '1') {
        toggleLayer('observations');
      } else if (e.key === '2') {
        toggleLayer('habitat');
      } else if (e.key === '3') {
        toggleLayer('corridors');
      } else if (e.key === '4') {
        toggleLayer('priority');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [project, selectedZone, showSimulation, handleExportData]);

  // ────────── Zone Selection & Map Focusing ──────────
  const handleZoneClick = (zone) => {
    setSelectedZone(zone);
  };

  const handleFocusZone = (zone) => {
    if (zone.geometry?.coordinates) {
      const ring = zone.geometry.coordinates[0];
      if (Array.isArray(ring) && ring.length > 0) {
        const pt = ring[0];
        setFocusCoords([pt[1], pt[0]]);
        addToast(`Centered map on Priority Zone #${zone.rank}`, 'info', 2000);
      }
    }
  };

  return (
    <div className="app-layout">
      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100vh' }}>
        <Header
          project={project}
          species={selectedSpecies}
          analysisStatus={analysisStatus}
          projectsList={projectsList}
          activeTab={activeTab}
          onSelectProject={handleSelectProject}
          onNewAnalysis={handleNewAnalysis}
          onExportData={handleExportData}
          onTabChange={setActiveTab}
          onOpenSimulation={() => setShowSimulation(true)}
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
            onFocusZone={handleFocusZone}
          />

          <div className="map-container">
            <ConservationMap
              layers={layers}
              onZoneClick={handleZoneClick}
              focusCoords={focusCoords}
              onOpenSimulation={() => setShowSimulation(true)}
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
