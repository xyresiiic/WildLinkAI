/**
 * WildLink AI — Sidebar Component
 */
import { useState } from 'react';
import {
  Map, Layers, Target, Zap, BarChart3,
  ChevronRight, Play, Eye, EyeOff, Settings
} from 'lucide-react';

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
          <div style={{ padding: '12px 16px 0' }}>
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

  return (
    <div className="sidebar-content" style={{ padding: '24px' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{
          width: 64, height: 64, borderRadius: 'var(--radius-lg)',
          background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-teal))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 16px', fontSize: '28px'
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

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {species.map(sp => (
          <div
            key={sp.id}
            onClick={() => setSelectedId(sp.id)}
            className="priority-item"
            style={{
              borderColor: selectedId === sp.id ? 'var(--color-primary)' : undefined,
              background: selectedId === sp.id ? 'var(--color-primary-glow)' : undefined,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{sp.common_name}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                  {sp.scientific_name}
                </div>
              </div>
              <span className={`badge badge-${sp.conservation_status === 'Endangered' ? 'critical' : 'medium'}`}>
                {sp.conservation_status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {selectedId && (
        <button
          className="btn btn-primary btn-lg"
          style={{ width: '100%', marginTop: '20px' }}
          onClick={() => onSelectSpecies(selectedId)}
        >
          <ChevronRight size={16} />
          Create Analysis Project
        </button>
      )}
    </div>
  );
}

// ────────────── Analysis Panel ──────────────
function AnalysisPanel({ dashboard, analysisStatus, analysisProgress, onRunAnalysis, onOpenSimulation }) {
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
            <div className="stat-label">Critical Zones</div>
          </div>
        </div>
      )}

      {/* More stats */}
      {dashboard && (
        <div className="card" style={{ marginBottom: '16px', padding: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Species</span>
            <span>{dashboard.species_name || '—'}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Region</span>
            <span>{dashboard.region_name || '—'}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Observations</span>
            <span>{dashboard.total_observations ?? 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '6px' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Habitat Patches</span>
            <span>{dashboard.total_habitat_patches ?? 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>Corridors</span>
            <span>{dashboard.total_corridors ?? 0}</span>
          </div>
        </div>
      )}

      {/* Analysis Controls */}
      {analysisStatus === 'running' ? (
        <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
          <div className="animate-pulse" style={{
            fontSize: '0.9rem', color: 'var(--color-accent-amber)', marginBottom: '12px'
          }}>
            <Zap size={20} style={{ marginBottom: '4px' }} />
            <div>Running Analysis Pipeline...</div>
          </div>
          <div className="score-bar" style={{ marginBottom: '8px' }}>
            <div
              className="score-bar-fill"
              style={{
                width: `${analysisProgress}%`,
                background: 'linear-gradient(90deg, var(--color-primary), var(--color-accent-teal))',
              }}
            />
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            {analysisProgress}% complete
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button className="btn btn-primary btn-lg" style={{ width: '100%' }} onClick={onRunAnalysis}>
            <Play size={16} />
            {analysisStatus === 'completed' ? 'Re-Run Analysis' : 'Run Full Analysis'}
          </button>
          {analysisStatus === 'completed' && (
            <button className="btn btn-secondary" style={{ width: '100%' }} onClick={onOpenSimulation}>
              <BarChart3 size={16} />
              Open What-If Simulator
            </button>
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 24, height: 8, borderRadius: 2, background: 'linear-gradient(90deg, #ef4444, #f97316, #eab308, #22c55e, #15803d)' }} />
              <span>Habitat Suitability (Low → High)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 24, height: 3, borderRadius: 2, background: '#3b82f6' }} />
              <span>Potential Corridor</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', border: '2px solid #ef4444', background: 'rgba(239, 68, 68, 0.2)' }} />
              <span>Priority Zone</span>
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
        <div>No priority zones yet.</div>
        <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>Run analysis to generate conservation priorities.</div>
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
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="rank">#{zone.rank || idx + 1}</span>
                  <span className={`badge badge-${zone.priority_level || 'medium'}`}>
                    {zone.priority_level || 'medium'}
                  </span>
                </div>
                <div className="explanation" style={{ marginTop: '6px' }}>
                  {zone.explanation?.substring(0, 120)}...
                </div>
              </div>
              <div className="score" style={{ textAlign: 'right', minWidth: '45px' }}>
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
