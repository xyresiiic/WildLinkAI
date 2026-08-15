/**
 * WildLink AI — Sidebar Component
 */
import { useState } from 'react';
import {
  Map, Layers, Target, Zap, BarChart3,
  ChevronRight, Play, Eye, EyeOff, AlertCircle
} from 'lucide-react';

// Map conservation status to badge class
function conservationBadgeClass(status) {
  if (!status) return 'badge-medium';
  const lower = status.toLowerCase();
  if (lower === 'endangered') return 'badge-endangered';
  if (lower === 'vulnerable') return 'badge-vulnerable';
  if (lower === 'critical' || lower === 'critically endangered') return 'badge-critical';
  if (lower === 'least concern') return 'badge-low';
  return 'badge-medium';
}

function Sidebar({
  species, selectedSpecies, project, dashboard, layers,
  activeTab, analysisStatus, analysisProgress, priorityZones,
  onSelectSpecies, onToggleLayer, onRunAnalysis, onTabChange,
  onZoneClick, onOpenSimulation
}) {
  return (
    <aside className="sidebar animate-slide-left">
      {!project ? (
        <SetupPanel species={species} onSelectSpecies={onSelectSpecies} />
      ) : (
        <>
          {/* Tabs */}
          <div style={{ padding: '12px 16px 0', flexShrink: 0 }}>
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
                onClick={() => onTabChange('analysis')}
              >
                <Map size={13} style={{ marginRight: 4 }} /> Analysis
              </button>
              <button
                className={`tab ${activeTab === 'layers' ? 'active' : ''}`}
                onClick={() => onTabChange('layers')}
              >
                <Layers size={13} style={{ marginRight: 4 }} /> Layers
              </button>
              <button
                className={`tab ${activeTab === 'priority' ? 'active' : ''}`}
                onClick={() => onTabChange('priority')}
              >
                <Target size={13} style={{ marginRight: 4 }} /> Priority
              </button>
            </div>
          </div>

          <div className="sidebar-content">
            {activeTab === 'analysis' && (
              <AnalysisPanel
                dashboard={dashboard}
                analysisStatus={analysisStatus}
                analysisProgress={analysisProgress}
                onRunAnalysis={onRunAnalysis}
                onOpenSimulation={onOpenSimulation}
              />
            )}
            {activeTab === 'layers' && (
              <LayerPanel layers={layers} onToggleLayer={onToggleLayer} />
            )}
            {activeTab === 'priority' && (
              <PriorityPanel
                zones={priorityZones}
                onZoneClick={onZoneClick}
                onOpenSimulation={onOpenSimulation}
              />
            )}
          </div>
        </>
      )}
    </aside>
  );
}

// ────────────── Setup Panel ──────────────
function SetupPanel({ species, onSelectSpecies }) {
  const [selectedId, setSelectedId] = useState(null);
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!selectedId || creating) return;
    setCreating(true);
    try {
      await onSelectSpecies(selectedId);
    } finally {
      setCreating(false);
    }
  };

  return (
    <>
      {/* Scrollable content */}
      <div className="sidebar-content">
        <div style={{ textAlign: 'center', marginBottom: '28px', paddingTop: '8px' }}>
          <div style={{
            width: 64, height: 64, borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-teal))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 16px', fontSize: '28px',
            boxShadow: '0 8px 24px rgba(34, 197, 94, 0.25)',
          }}>
            🐾
          </div>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontWeight: 700,
            fontSize: '1.4rem', marginBottom: '8px'
          }}>
            Start Conservation Analysis
          </h2>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>
            Select a focal species to begin habitat connectivity analysis
            in the Central Indian Highlands.
          </p>
        </div>

        <div className="section-header">
          <span className="section-title">Select Species</span>
        </div>

        {species.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--color-text-muted)' }}>
            <div className="spinner" style={{ margin: '0 auto 12px', color: 'var(--color-primary)' }} />
            <div style={{ fontSize: '0.85rem' }}>Loading species...</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {species.map(sp => (
              <div
                key={sp.id}
                onClick={() => setSelectedId(sp.id)}
                className="priority-item"
                style={{
                  borderColor: selectedId === sp.id ? 'var(--color-primary)' : undefined,
                  background: selectedId === sp.id ? 'var(--color-primary-glow)' : undefined,
                  cursor: 'pointer',
                  userSelect: 'none',
                  boxShadow: selectedId === sp.id ? '0 0 0 1px var(--color-primary)' : undefined,
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {selectedId === sp.id && (
                        <span style={{ color: 'var(--color-primary)', fontSize: '0.7rem' }}>✓</span>
                      )}
                      {sp.common_name}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                      {sp.scientific_name}
                    </div>
                  </div>
                  <span className={`badge ${conservationBadgeClass(sp.conservation_status)}`}>
                    {sp.conservation_status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sticky footer button */}
      <div className="sidebar-footer">
        <button
          id="create-project-btn"
          className="btn btn-primary btn-lg"
          style={{ width: '100%' }}
          onClick={handleCreate}
          disabled={!selectedId || creating}
        >
          {creating ? (
            <>
              <span className="spinner" />
              Setting up project...
            </>
          ) : (
            <>
              <ChevronRight size={16} />
              {selectedId ? 'Create Analysis Project' : 'Select a Species First'}
            </>
          )}
        </button>
      </div>
    </>
  );
}

// ────────────── Analysis Panel ──────────────
function AnalysisPanel({ dashboard, analysisStatus, analysisProgress, onRunAnalysis, onOpenSimulation }) {
  const [runningLocally, setRunningLocally] = useState(false);

  const handleRunAnalysis = async () => {
    if (runningLocally) return;
    setRunningLocally(true);
    try {
      await onRunAnalysis();
    } finally {
      // runningLocally will be reset naturally when analysisStatus changes
      setRunningLocally(false);
    }
  };

  const isRunning = analysisStatus === 'running';

  return (
    <div className="animate-fade-in">
      {/* Dashboard Stats */}
      {dashboard && (
        <div className="stats-grid" style={{ marginBottom: '16px' }}>
          <div className="stat-card">
            <div className="stat-value">{dashboard.habitat_score ?? '—'}</div>
            <div className="stat-label">Habitat Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{dashboard.connectivity_score ?? '—'}</div>
            <div className="stat-label">Connectivity</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{dashboard.total_priority_zones ?? 0}</div>
            <div className="stat-label">Priority Zones</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{dashboard.critical_zones ?? 0}</div>
            <div className="stat-label">Critical</div>
          </div>
        </div>
      )}

      {/* More stats */}
      {dashboard && (
        <div className="card" style={{ marginBottom: '16px', padding: '14px' }}>
          {[
            ['Species', dashboard.species_name || '—'],
            ['Region', dashboard.region_name || '—'],
            ['Observations', dashboard.total_observations ?? 0],
            ['Habitat Patches', dashboard.total_habitat_patches ?? 0],
            ['Corridors', dashboard.total_corridors ?? 0],
          ].map(([label, value]) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>{label}</span>
              <span style={{ fontWeight: 500 }}>{value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Analysis Controls */}
      {isRunning ? (
        <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
          <div style={{
            fontSize: '0.9rem', color: 'var(--color-accent-amber)', marginBottom: '12px',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
          }}>
            <Zap size={16} />
            <span>Running Analysis Pipeline...</span>
          </div>
          <div className="score-bar" style={{ marginBottom: '8px' }}>
            <div
              className="score-bar-fill"
              style={{
                width: `${analysisProgress}%`,
                background: 'linear-gradient(90deg, var(--color-primary), var(--color-accent-teal))',
                transition: 'width 0.5s ease',
              }}
            />
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            {analysisProgress}% complete
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {analysisStatus === 'failed' && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 12px',
              background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)',
              borderRadius: 'var(--radius-md)', fontSize: '0.8rem', color: '#f87171',
              marginBottom: '8px',
            }}>
              <AlertCircle size={14} />
              <span>Analysis failed. Check connection and retry.</span>
            </div>
          )}
          <button
            id="run-analysis-btn"
            className="btn btn-primary btn-lg"
            style={{ width: '100%' }}
            onClick={handleRunAnalysis}
            disabled={runningLocally}
          >
            {runningLocally ? (
              <><span className="spinner" /> Starting...</>
            ) : (
              <><Play size={16} />{analysisStatus === 'completed' ? 'Re-Run Analysis' : 'Run Full Analysis'}</>
            )}
          </button>
          {analysisStatus === 'completed' && (
            <button
              id="open-simulator-btn"
              className="btn btn-secondary"
              style={{ width: '100%' }}
              onClick={onOpenSimulation}
            >
              <BarChart3 size={16} />
              Open What-If Simulator
            </button>
          )}
          {!dashboard && analysisStatus !== 'completed' && (
            <p style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: '8px', lineHeight: 1.5 }}>
              Run the full analysis pipeline to generate habitat zones, corridors, and priority rankings.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ────────────── Layer Panel ──────────────
function LayerPanel({ layers, onToggleLayer }) {
  const layerConfig = [
    { key: 'observations', label: 'Species Observations', color: '#f59e0b', icon: '📍' },
    { key: 'habitat', label: 'Habitat Suitability', color: '#22c55e', icon: '🌿' },
    { key: 'corridors', label: 'Connectivity Corridors', color: '#3b82f6', icon: '🔗' },
    { key: 'priority', label: 'Priority Zones', color: '#ef4444', icon: '🎯' },
  ];

  return (
    <div className="animate-fade-in">
      <div className="section-header">
        <span className="section-title">Map Layers</span>
      </div>

      <div className="layer-controls">
        {layerConfig.map(({ key, label, color, icon }) => (
          <label key={key} className="layer-toggle">
            <input
              type="checkbox"
              checked={layers[key]?.visible ?? false}
              onChange={() => onToggleLayer(key)}
            />
            <span className="layer-color-dot" style={{ background: color }} />
            <span style={{ fontSize: '0.85rem' }}>{icon} {label}</span>
            {layers[key]?.data && (
              <span style={{
                marginLeft: 'auto',
                fontSize: '0.7rem',
                color: 'var(--color-text-muted)',
                background: 'var(--color-bg-primary)',
                padding: '1px 6px',
                borderRadius: 'var(--radius-full)',
              }}>
                {layers[key].data.count || layers[key].data.features?.length || 0}
              </span>
            )}
          </label>
        ))}
      </div>

      <div style={{ marginTop: '20px' }}>
        <div className="section-header">
          <span className="section-title">Legend</span>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 32, height: 8, borderRadius: 2, background: 'linear-gradient(90deg, #ef4444, #f97316, #eab308, #22c55e, #15803d)', flexShrink: 0 }} />
              <span>Habitat Suitability (Low → High)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 24, height: 3, borderRadius: 2, background: '#3b82f6', flexShrink: 0 }} />
              <span>Potential Corridor</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', border: '2px solid #ef4444', background: 'rgba(239, 68, 68, 0.2)', flexShrink: 0 }} />
              <span>Priority Zone</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#fbbf24', flexShrink: 0 }} />
              <span>Species Observation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ────────────── Priority Panel ──────────────
function PriorityPanel({ zones, onZoneClick, onOpenSimulation }) {
  if (!zones || zones.length === 0) {
    return (
      <div className="animate-fade-in" style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--color-text-muted)' }}>
        <Target size={40} style={{ opacity: 0.3, marginBottom: '12px' }} />
        <div style={{ fontWeight: 500, marginBottom: '4px' }}>No priority zones yet.</div>
        <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>Run the analysis to generate conservation priorities.</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="section-header">
        <span className="section-title">Conservation Priorities</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{zones.length} zones</span>
      </div>

      <div className="priority-list">
        {zones.map((zone, idx) => (
          <div
            key={zone.id || idx}
            className={`priority-item ${zone.priority_level || 'medium'}`}
            onClick={() => onZoneClick(zone)}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && onZoneClick(zone)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="rank">#{zone.rank || idx + 1}</span>
                  <span className={`badge badge-${zone.priority_level || 'medium'}`}>
                    {zone.priority_level || 'medium'}
                  </span>
                </div>
                <div className="explanation">
                  {zone.explanation?.substring(0, 110)}{zone.explanation?.length > 110 ? '...' : ''}
                </div>
              </div>
              <div className="score" style={{ textAlign: 'right', minWidth: '48px', flexShrink: 0, marginLeft: '8px' }}>
                <div style={{
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  color: zone.priority_score >= 70 ? 'var(--color-critical)' :
                         zone.priority_score >= 50 ? 'var(--color-high)' : 'var(--color-primary-light)'
                }}>
                  {zone.priority_score?.toFixed(0)}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>/100</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {zones.length > 0 && (
        <button
          id="compare-scenarios-btn"
          className="btn btn-primary"
          style={{ width: '100%', marginTop: '16px' }}
          onClick={onOpenSimulation}
        >
          <BarChart3 size={16} />
          Compare Scenarios
        </button>
      )}
    </div>
  );
}

export default Sidebar;
