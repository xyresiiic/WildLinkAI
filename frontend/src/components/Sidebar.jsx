/**
 * WildLink AI — Sidebar Component
 */
import { useState, useMemo } from 'react';
import {
  Map, Layers, Target, Zap, BarChart3,
  ChevronRight, Play, Eye, EyeOff, AlertCircle,
  Search, Filter, ArrowUpDown, Crosshair, Sparkles
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

function getSpeciesCategory(sp) {
  const name = (sp.common_name + ' ' + (sp.scientific_name || '')).toLowerCase();
  if (name.includes('bustard') || name.includes('bird')) return 'Birds';
  if (name.includes('gharial') || name.includes('croc') || name.includes('turtle')) return 'Reptiles';
  if (name.includes('snow leopard')) return 'Alpine';
  return 'Mammals';
}

function getSpeciesEmoji(sp) {
  const name = (sp.common_name || '').toLowerCase();
  if (name.includes('tiger')) return '🐅';
  if (name.includes('elephant')) return '🐘';
  if (name.includes('leopard') && !name.includes('snow')) return '🐆';
  if (name.includes('snow leopard')) return '❄️🐆';
  if (name.includes('bear')) return '🐻';
  if (name.includes('bustard')) return '🦅';
  if (name.includes('gharial')) return '🐊';
  return '🐾';
}

function Sidebar({
  species, selectedSpecies, project, dashboard, layers,
  activeTab, analysisStatus, analysisProgress, priorityZones,
  onSelectSpecies, onToggleLayer, onRunAnalysis, onTabChange,
  onZoneClick, onOpenSimulation, onFocusZone
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
                <Target size={13} style={{ marginRight: 4 }} /> Priorities ({priorityZones?.length || 0})
              </button>
            </div>
          </div>

          <div className="sidebar-content">
            {activeTab === 'analysis' && (
              <AnalysisPanel
                project={project}
                selectedSpecies={selectedSpecies}
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
                onFocusZone={onFocusZone}
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
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const categories = ['All', 'Mammals', 'Birds', 'Reptiles', 'Alpine'];

  const filteredSpecies = useMemo(() => {
    return species.filter(sp => {
      const matchesSearch =
        sp.common_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        sp.scientific_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (sp.conservation_status || '').toLowerCase().includes(searchQuery.toLowerCase());

      const cat = getSpeciesCategory(sp);
      const matchesCategory = categoryFilter === 'All' || cat === categoryFilter;

      return matchesSearch && matchesCategory;
    });
  }, [species, searchQuery, categoryFilter]);

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
      <div className="sidebar-content">
        <div style={{ textAlign: 'center', marginBottom: '20px', paddingTop: '6px' }}>
          <div style={{
            width: 56, height: 56, borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-teal))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 12px', fontSize: '24px',
            boxShadow: '0 8px 24px rgba(34, 197, 94, 0.25)',
          }}>
            🌿
          </div>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontWeight: 700,
            fontSize: '1.3rem', marginBottom: '6px'
          }}>
            Conservation Intelligence
          </h2>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.82rem', lineHeight: 1.5 }}>
            Select a target species to model habitat suitability, fragmentation, wildlife corridors, and priority zones.
          </p>
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', marginBottom: '12px' }}>
          <Search size={14} style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
          <input
            type="text"
            className="form-input"
            placeholder="Search species (e.g. Tiger, Gharial, Bustard)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '32px', fontSize: '0.82rem' }}
          />
        </div>

        {/* Category Pills */}
        <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '8px', marginBottom: '12px' }}>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              style={{
                padding: '4px 10px', borderRadius: 'var(--radius-full)',
                border: '1px solid',
                borderColor: categoryFilter === cat ? 'var(--color-primary)' : 'var(--color-border)',
                background: categoryFilter === cat ? 'var(--color-primary-glow)' : 'transparent',
                color: categoryFilter === cat ? 'var(--color-primary-light)' : 'var(--color-text-muted)',
                fontSize: '0.72rem', fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Species List */}
        {species.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--color-text-muted)' }}>
            <div className="spinner" style={{ margin: '0 auto 12px', color: 'var(--color-primary)' }} />
            <div style={{ fontSize: '0.85rem' }}>Loading species catalogue...</div>
          </div>
        ) : filteredSpecies.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '24px 16px', color: 'var(--color-text-muted)', fontSize: '0.82rem' }}>
            No species matching "{searchQuery}"
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredSpecies.map(sp => {
              const isSelected = selectedId === sp.id;
              const emoji = getSpeciesEmoji(sp);
              return (
                <div
                  key={sp.id}
                  onClick={() => setSelectedId(sp.id)}
                  className="priority-item"
                  style={{
                    borderColor: isSelected ? 'var(--color-primary)' : undefined,
                    background: isSelected ? 'var(--color-primary-glow)' : undefined,
                    boxShadow: isSelected ? '0 0 0 1px var(--color-primary)' : undefined,
                    cursor: 'pointer',
                    userSelect: 'none',
                    transition: 'all 0.15s ease',
                    padding: '12px 14px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '10px' }}>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                      <span style={{ fontSize: '1.4rem' }}>{emoji}</span>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.92rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {isSelected && (
                            <span style={{ color: 'var(--color-primary)', fontSize: '0.75rem' }}>✓</span>
                          )}
                          {sp.common_name}
                        </div>
                        <div style={{ fontSize: '0.76rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                          {sp.scientific_name}
                        </div>
                      </div>
                    </div>
                    <span className={`badge ${conservationBadgeClass(sp.conservation_status)}`} style={{ fontSize: '0.68rem' }}>
                      {sp.conservation_status}
                    </span>
                  </div>

                  {sp.description && (
                    <div style={{ fontSize: '0.76rem', color: 'var(--color-text-secondary)', marginTop: '8px', lineHeight: 1.4 }}>
                      {sp.description.substring(0, 95)}...
                    </div>
                  )}
                </div>
              );
            })}
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
              {selectedId ? 'Start Conservation Analysis' : 'Select a Target Species'}
            </>
          )}
        </button>
      </div>
    </>
  );
}

// ────────────── Analysis Panel ──────────────
function AnalysisPanel({ project, selectedSpecies, dashboard, analysisStatus, analysisProgress, onRunAnalysis, onOpenSimulation }) {
  const [runningLocally, setRunningLocally] = useState(false);

  const handleRunAnalysis = async () => {
    if (runningLocally) return;
    setRunningLocally(true);
    try {
      await onRunAnalysis();
    } finally {
      setRunningLocally(false);
    }
  };

  const isRunning = analysisStatus === 'running';

  return (
    <div className="animate-fade-in">
      {/* Species & Region Banner */}
      {selectedSpecies && (
        <div style={{
          background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(20, 184, 166, 0.05))',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          padding: '12px 14px', marginBottom: '16px',
          display: 'flex', alignItems: 'center', gap: '10px',
        }}>
          <span style={{ fontSize: '1.6rem' }}>{getSpeciesEmoji(selectedSpecies)}</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{selectedSpecies.common_name}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              {project?.region_name || 'Central Indian Highlands'} • <span className={`badge ${conservationBadgeClass(selectedSpecies.conservation_status)}`} style={{ fontSize: '0.65rem' }}>{selectedSpecies.conservation_status}</span>
            </div>
          </div>
        </div>
      )}

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

      {/* Breakdown Card */}
      {dashboard && (
        <div className="card" style={{ marginBottom: '16px', padding: '14px' }}>
          {[
            ['Species Observations', dashboard.total_observations ?? 0],
            ['Habitat Patches Identified', dashboard.total_habitat_patches ?? 0],
            ['Connectivity Corridors', dashboard.total_corridors ?? 0],
            ['Critical Priority Zones', dashboard.critical_zones ?? 0],
          ].map(([label, value]) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '8px' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>{label}</span>
              <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{value}</span>
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
            <span>Running AI Analysis Pipeline...</span>
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
              <span>Analysis encountered an issue. Check connection and retry.</span>
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
              <><Play size={16} />{analysisStatus === 'completed' ? 'Re-Run Analysis Pipeline' : 'Run Full AI Analysis'}</>
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
              Click to execute suitability estimation, graph connectivity modeling, and conservation priority ranking.
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
    { key: 'corridors', label: 'Least-Cost Corridors', color: '#3b82f6', icon: '🔗' },
    { key: 'priority', label: 'Conservation Priority Zones', color: '#ef4444', icon: '🎯' },
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
          <span className="section-title">Legend & Symbology</span>
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 36, height: 8, borderRadius: 2, background: 'linear-gradient(90deg, #ef4444, #f97316, #eab308, #22c55e, #15803d)', flexShrink: 0 }} />
              <span>Habitat Suitability (Low → High)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 26, height: 4, borderRadius: 2, background: '#3b82f6', flexShrink: 0 }} />
              <span>Least-Cost Movement Corridor</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 12, height: 12, borderRadius: '4px', border: '2px dashed #ef4444', background: 'rgba(239, 68, 68, 0.25)', flexShrink: 0 }} />
              <span>Priority Intervention Zone</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#fbbf24', flexShrink: 0 }} />
              <span>Confirmed Species Occurrence</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ────────────── Priority Panel ──────────────
function PriorityPanel({ zones, onZoneClick, onOpenSimulation, onFocusZone }) {
  const [filterLevel, setFilterLevel] = useState('all');
  const [sortBy, setSortBy] = useState('rank');
  const [search, setSearch] = useState('');

  const filteredZones = useMemo(() => {
    if (!zones) return [];
    let list = zones.filter(z => {
      const matchLevel = filterLevel === 'all' || z.priority_level === filterLevel;
      const matchSearch = !search ||
        (z.explanation || '').toLowerCase().includes(search.toLowerCase()) ||
        (z.dominant_factor || '').toLowerCase().includes(search.toLowerCase()) ||
        (z.recommended_action || '').toLowerCase().includes(search.toLowerCase());
      return matchLevel && matchSearch;
    });

    if (sortBy === 'score') {
      list.sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    } else if (sortBy === 'area') {
      list.sort((a, b) => (b.area_hectares || 0) - (a.area_hectares || 0));
    } else {
      list.sort((a, b) => (a.rank || 0) - (b.rank || 0));
    }

    return list;
  }, [zones, filterLevel, sortBy, search]);

  if (!zones || zones.length === 0) {
    return (
      <div className="animate-fade-in" style={{ textAlign: 'center', padding: '32px 16px', color: 'var(--color-text-muted)' }}>
        <Target size={40} style={{ opacity: 0.3, marginBottom: '12px' }} />
        <div style={{ fontWeight: 500, marginBottom: '4px' }}>No priority zones generated yet.</div>
        <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>Run the AI analysis pipeline to calculate conservation rankings.</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="section-header">
        <span className="section-title">Intervention Priorities</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{filteredZones.length} of {zones.length} zones</span>
      </div>

      {/* Filter Chips & Search */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '12px' }}>
        <input
          type="text"
          className="form-input"
          placeholder="Filter by action or factor..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ fontSize: '0.78rem', padding: '6px 10px' }}
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '4px' }}>
            {['all', 'critical', 'high', 'medium'].map(lvl => (
              <button
                key={lvl}
                onClick={() => setFilterLevel(lvl)}
                style={{
                  padding: '2px 8px', borderRadius: 'var(--radius-sm)',
                  fontSize: '0.7rem', fontWeight: 600, textTransform: 'capitalize',
                  border: '1px solid',
                  borderColor: filterLevel === lvl ? 'var(--color-primary)' : 'var(--color-border)',
                  background: filterLevel === lvl ? 'var(--color-primary-glow)' : 'transparent',
                  color: filterLevel === lvl ? 'var(--color-primary-light)' : 'var(--color-text-muted)',
                  cursor: 'pointer',
                }}
              >
                {lvl}
              </button>
            ))}
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              background: 'var(--color-bg-secondary)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
              fontSize: '0.7rem', borderRadius: 'var(--radius-sm)',
              padding: '2px 6px',
            }}
          >
            <option value="rank">Sort by Rank</option>
            <option value="score">Sort by Score</option>
            <option value="area">Sort by Area</option>
          </select>
        </div>
      </div>

      {/* Priority Cards List */}
      <div className="priority-list">
        {filteredZones.map((zone, idx) => (
          <div
            key={zone.id || idx}
            className={`priority-item ${zone.priority_level || 'medium'}`}
            onClick={() => onZoneClick(zone)}
            role="button"
            tabIndex={0}
            onKeyDown={e => e.key === 'Enter' && onZoneClick(zone)}
            style={{ position: 'relative' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                  <span className="rank">#{zone.rank || idx + 1}</span>
                  <span className={`badge badge-${zone.priority_level || 'medium'}`} style={{ fontSize: '0.65rem' }}>
                    {zone.priority_level || 'medium'}
                  </span>
                  {zone.area_hectares && (
                    <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                      • {zone.area_hectares.toFixed(0)} ha
                    </span>
                  )}
                </div>

                {zone.recommended_action && (
                  <div style={{
                    fontSize: '0.76rem', fontWeight: 600, color: 'var(--color-primary-light)',
                    marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px',
                  }}>
                    <Sparkles size={12} />
                    <span>{zone.recommended_action}</span>
                  </div>
                )}

                <div className="explanation" style={{ fontSize: '0.76rem', lineHeight: 1.4 }}>
                  {zone.explanation?.substring(0, 95)}{zone.explanation?.length > 95 ? '...' : ''}
                </div>
              </div>

              <div className="score" style={{ textAlign: 'right', minWidth: '48px', flexShrink: 0, marginLeft: '8px' }}>
                <div style={{
                  fontSize: '1.15rem',
                  fontWeight: 800,
                  color: zone.priority_score >= 70 ? 'var(--color-critical)' :
                         zone.priority_score >= 50 ? 'var(--color-high)' : 'var(--color-primary-light)'
                }}>
                  {zone.priority_score?.toFixed(0)}
                </div>
                <div style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)' }}>/100</div>

                {onFocusZone && zone.geometry && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onFocusZone(zone);
                    }}
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: 'var(--color-primary-light)', marginTop: 4, padding: 2,
                    }}
                    title="Center on Map"
                  >
                    <Crosshair size={13} />
                  </button>
                )}
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
          Simulate Restoration Scenarios
        </button>
      )}
    </div>
  );
}

export default Sidebar;

