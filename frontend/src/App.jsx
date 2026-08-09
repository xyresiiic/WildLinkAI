/**
 * WildLink AI — Main App Component
 */
import { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ConservationMap from './components/Map/ConservationMap';
import ZoneDetailModal from './components/ZoneDetailModal';
import SimulationPanel from './components/SimulationPanel';
import {
  getSpecies, getProjects, createProject, getDashboard,
  runAnalysis, getJobStatus, getHabitatZones, getCorridors,
  getPriorityZones, getObservations
} from './services/api';
import './App.css';

function App() {
  // ────────── State ──────────
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
  const [analysisStatus, setAnalysisStatus] = useState('idle'); // idle, running, completed, failed
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [selectedZone, setSelectedZone] = useState(null);
  const [showSimulation, setShowSimulation] = useState(false);

  // Priority zones
  const [priorityZones, setPriorityZones] = useState([]);

  // ────────── Load initial data ──────────
  useEffect(() => {
    loadSpecies();
  }, []);

  const loadSpecies = async () => {
    try {
      const res = await getSpecies();
      setSpecies(res.data.data || []);
    } catch (err) {
      console.error('Failed to load species:', err);
    }
  };

  // ────────── Project Creation ──────────
  const handleCreateProject = async (speciesId) => {
    try {
      const sp = species.find(s => s.id === speciesId);
      const res = await createProject({
        name: `${sp?.common_name || 'Wildlife'} Corridor Analysis`,
        description: `Habitat connectivity analysis for ${sp?.common_name || 'target species'} in Central Indian Highlands`,
        region_name: 'Central Indian Highlands',
        species_id: speciesId,
      });

      const proj = res.data.data;
      setProject(proj);
      setSelectedSpecies(sp);

      // Load dashboard
      const dashRes = await getDashboard(proj.id);
      setDashboard(dashRes.data.data);
    } catch (err) {
      console.error('Failed to create project:', err);
    }
  };

  // ────────── Run Analysis ──────────
  const handleRunAnalysis = async () => {
    if (!project) return;

    setAnalysisStatus('running');
    setAnalysisProgress(0);

    try {
      const res = await runAnalysis({
        project_id: project.id,
        type: 'full',
      });

      const jobId = res.data.data?.id;
      if (jobId) {
        pollJobStatus(jobId);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      setAnalysisStatus('failed');
    }
  };

  const pollJobStatus = async (jobId) => {
    const poll = setInterval(async () => {
      try {
        const res = await getJobStatus(jobId);
        const job = res.data.data;

        setAnalysisProgress(job.progress || 0);

        if (job.status === 'completed') {
          clearInterval(poll);
          setAnalysisStatus('completed');
          await loadAnalysisResults();
        } else if (job.status === 'failed') {
          clearInterval(poll);
          setAnalysisStatus('failed');
        }
      } catch (err) {
        clearInterval(poll);
        setAnalysisStatus('failed');
      }
    }, 2000);
  };

  // ────────── Load Results ──────────
  const loadAnalysisResults = async () => {
    if (!project) return;

    try {
      const [habitatRes, corridorRes, priorityRes, obsRes, dashRes] = await Promise.all([
        getHabitatZones(project.id),
        getCorridors(project.id),
        getPriorityZones(project.id),
        getObservations(project.id).catch(() => ({ data: { data: { features: [] } } })),
        getDashboard(project.id),
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
    }
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
    </div>
  );
}

export default App;
