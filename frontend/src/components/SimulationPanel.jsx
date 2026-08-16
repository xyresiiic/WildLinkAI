/**
 * WildLink AI — What-If Simulation Panel
 */
import { useState, useEffect } from 'react';
import { X, Play, BarChart3, TrendingUp, AlertTriangle, Sparkles, CheckSquare, Layers } from 'lucide-react';
import { createSimulation, getProjectSimulations, getSimulation } from '../services/api';

const INTERVENTION_TYPES = [
  { id: 'habitat_restoration', label: '🌿 Corridor Reforestation', desc: 'Planting native vegetation and riparian buffers' },
  { id: 'wildlife_crossing', label: '🌉 Highway Eco-Duct / Overpass', desc: 'Mitigating road barriers & vehicle collisions' },
  { id: 'protected_area_expansion', label: '🛡️ Core Buffer Expansion', desc: 'Designating strict legal wildlife protections' },
  { id: 'community_conservation', label: '🤝 Community HWC Mitigation', desc: 'Agroforestry and local conflict reduction' },
];

function SimulationPanel({ project, priorityZones, onClose }) {
  const [selectedZones, setSelectedZones] = useState([]);
  const [interventionType, setInterventionType] = useState('habitat_restoration');
  const [intensity, setIntensity] = useState(1.0);
  const [scenarioName, setScenarioName] = useState('');
  const [simulating, setSimulating] = useState(false);
  const [scenarios, setScenarios] = useState([]);
  const [baseline, setBaseline] = useState(null);

  // Load existing simulations and pre-select top 3 zones
  useEffect(() => {
    loadScenarios();
    if (priorityZones && priorityZones.length > 0 && selectedZones.length === 0) {
      setSelectedZones(priorityZones.slice(0, 3).map(z => z.id));
    }
  }, [project.id, priorityZones]);

  const loadScenarios = async () => {
    try {
      const res = await getProjectSimulations(project.id);
      const data = res.data.data;
      setScenarios(data.scenarios || []);
      setBaseline(data.baseline_connectivity || null);
    } catch (err) {
      console.error('Failed to load scenarios:', err);
    }
  };

  const toggleZone = (zoneId) => {
    setSelectedZones(prev =>
      prev.includes(zoneId)
        ? prev.filter(id => id !== zoneId)
        : [...prev, zoneId]
    );
  };

  const selectTopZones = (count) => {
    const topIds = (priorityZones || []).slice(0, count).map(z => z.id);
    setSelectedZones(topIds);
  };

  const handleSimulate = async () => {
    setSimulating(true);
    try {
      const zoneCount = selectedZones.length > 0 ? selectedZones.length : Math.min(3, priorityZones?.length || 3);
      const defaultName = `${INTERVENTION_TYPES.find(t => t.id === interventionType)?.label.split(' ')[1] || 'Scenario'} on ${zoneCount} Zone${zoneCount === 1 ? '' : 's'}`;

      const res = await createSimulation({
        project_id: project.id,
        name: scenarioName.trim() || defaultName,
        intervention_type: interventionType,
        zone_ids: selectedZones.length > 0 ? selectedZones : undefined,
        parameters: { intensity },
      });

      const simId = res.data.data?.id;
      if (simId) {
        await pollSimulation(simId);
        setScenarioName('');
      }
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  const pollSimulation = async (simId) => {
    return new Promise((resolve) => {
      let consecutiveErrors = 0;
      const poll = setInterval(async () => {
        try {
          const res = await getSimulation(simId);
          const sim = res.data.data;
          consecutiveErrors = 0;
          if (sim.status === 'completed' || sim.status === 'failed') {
            clearInterval(poll);
            await loadScenarios();
            resolve();
          }
        } catch (err) {
          consecutiveErrors++;
          if (consecutiveErrors > 15) {
            clearInterval(poll);
            resolve();
          }
        }
      }, 1200);
    });
  };

  return (
    <div style={{
      position: 'fixed', top: 0, right: 0, bottom: 0,
      width: '440px', background: 'var(--color-bg-secondary)',
      borderLeft: '1px solid var(--color-border)',
      zIndex: 1500, display: 'flex', flexDirection: 'column',
      boxShadow: '-8px 0 32px rgba(0,0,0,0.5)',
    }} className="animate-slide-right">
      {/* Header */}
      <div style={{
        padding: '16px 20px', borderBottom: '1px solid var(--color-border)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.15rem' }}>
            🔬 What-If Conservation Simulator
          </div>
          <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
            Compare restoration & connectivity interventions
          </div>
        </div>
        <button onClick={onClose} style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: 'var(--color-text-muted)', padding: '4px',
        }}>
          <X size={20} />
        </button>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>
        {/* Disclaimer Banner */}
        <div style={{
          background: 'rgba(234, 179, 8, 0.08)', border: '1px solid rgba(234, 179, 8, 0.2)',
          borderRadius: 'var(--radius-md)', padding: '10px 12px',
          fontSize: '0.74rem', color: 'var(--color-accent-amber)',
          display: 'flex', gap: '8px', alignItems: 'start',
          marginBottom: '16px', lineHeight: 1.4,
        }}>
          <AlertTriangle size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>Simulations calculate theoretical graph connectivity gains on resistance surfaces to test conservation strategies before field deployment.</span>
        </div>

        {/* Create Scenario Section */}
        <div className="section-header">
          <span className="section-title">Configure Scenario</span>
        </div>

        {/* Intervention Type Selector */}
        <div className="form-group">
          <label className="form-label">Intervention Strategy</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {INTERVENTION_TYPES.map(t => (
              <div
                key={t.id}
                onClick={() => setInterventionType(t.id)}
                style={{
                  padding: '8px 10px', borderRadius: 'var(--radius-sm)',
                  border: '1px solid',
                  borderColor: interventionType === t.id ? 'var(--color-primary)' : 'var(--color-border)',
                  background: interventionType === t.id ? 'var(--color-primary-glow)' : 'var(--color-bg-card)',
                  cursor: 'pointer', transition: 'all 0.15s ease',
                }}
              >
                <div style={{ fontSize: '0.82rem', fontWeight: 600, color: interventionType === t.id ? 'var(--color-primary-light)' : 'var(--color-text-primary)' }}>
                  {t.label}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', marginTop: 2 }}>
                  {t.desc}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Intensity / Effort Slider */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 4 }}>
            <label className="form-label" style={{ marginBottom: 0 }}>Intervention Intensity</label>
            <span style={{ color: 'var(--color-primary-light)', fontWeight: 600 }}>{intensity}x</span>
          </div>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.25"
            value={intensity}
            onChange={(e) => setIntensity(parseFloat(e.target.value))}
            style={{ width: '100%', accentColor: 'var(--color-primary)', cursor: 'pointer' }}
          />
        </div>

        {/* Custom Name */}
        <div className="form-group">
          <label className="form-label">Scenario Name (Optional)</label>
          <input
            type="text"
            className="form-input"
            placeholder="e.g. Eco-duct across NH-44 on Zone #1"
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
            style={{ fontSize: '0.82rem' }}
          />
        </div>

        {/* Target Zones Checkbox List */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <label className="form-label" style={{ marginBottom: 0 }}>Target Intervention Zones</label>
            <div style={{ display: 'flex', gap: 6 }}>
              <button
                type="button"
                onClick={() => selectTopZones(3)}
                style={{ background: 'none', border: 'none', color: 'var(--color-primary-light)', fontSize: '0.72rem', cursor: 'pointer', fontWeight: 600 }}
              >
                Top 3
              </button>
              <span style={{ color: 'var(--color-text-muted)', fontSize: '0.72rem' }}>•</span>
              <button
                type="button"
                onClick={() => setSelectedZones([])}
                style={{ background: 'none', border: 'none', color: 'var(--color-text-muted)', fontSize: '0.72rem', cursor: 'pointer' }}
              >
                Clear
              </button>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '160px', overflowY: 'auto' }}>
            {priorityZones.slice(0, 10).map((zone, idx) => (
              <label
                key={zone.id || idx}
                className="layer-toggle"
                style={{
                  background: selectedZones.includes(zone.id)
                    ? 'var(--color-primary-glow)' : 'var(--color-bg-card)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid',
                  borderColor: selectedZones.includes(zone.id)
                    ? 'var(--color-primary)' : 'var(--color-border)',
                  padding: '6px 10px',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedZones.includes(zone.id)}
                  onChange={() => toggleZone(zone.id)}
                />
                <span style={{ fontSize: '0.8rem', fontWeight: 500 }}>
                  Zone #{zone.rank || idx + 1} (Score: {zone.priority_score?.toFixed(0)})
                </span>
                <span className={`badge badge-${zone.priority_level}`} style={{ marginLeft: 'auto', fontSize: '0.65rem' }}>
                  {zone.priority_level}
                </span>
              </label>
            ))}
          </div>
        </div>

        <button
          className="btn btn-primary"
          style={{ width: '100%', marginBottom: '24px' }}
          onClick={handleSimulate}
          disabled={simulating}
        >
          {simulating ? (
            <><span className="spinner" /> Simulating Connectivity Impact...</>
          ) : (
            <><Play size={14} /> Run What-If Simulation</>
          )}
        </button>

        {/* Scenario Comparison */}
        {scenarios.length > 0 && (
          <>
            <div className="section-header">
              <span className="section-title">Scenario Comparison</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{scenarios.length} scenarios</span>
            </div>

            {/* Baseline */}
            {baseline !== null && (
              <div className="scenario-card" style={{ marginBottom: '12px', borderLeft: '3px solid var(--color-text-secondary)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                      BASELINE LANDSCAPE
                    </div>
                    <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '0.92rem' }}>
                      Current Landscape Connectivity
                    </div>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-display)', fontWeight: 800,
                    fontSize: '1.5rem', color: 'var(--color-text-secondary)'
                  }}>
                    {baseline?.toFixed(1)}
                  </div>
                </div>
              </div>
            )}

            {/* Scenarios */}
            <div className="scenario-comparison">
              {scenarios.filter(s => s.status === 'completed').map((scenario, idx) => {
                const improvement = scenario.improvement || 0;
                const pctChange = scenario.percentage_change || 0;
                const isPositive = improvement > 0;

                return (
                  <div key={scenario.id || idx} className="scenario-card" style={{
                    borderLeft: `3px solid ${isPositive ? 'var(--color-primary)' : 'var(--color-border)'}`
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
                          Scenario {idx + 1}
                        </div>
                        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '0.92rem', marginTop: 1 }}>
                          {scenario.name}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{
                          fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '1.35rem',
                          color: 'var(--color-text-primary)'
                        }}>
                          {scenario.simulated_connectivity?.toFixed(1)}
                        </div>
                        <div className={`scenario-delta ${isPositive ? 'positive' : 'negative'}`}
                          style={{ fontSize: '0.82rem', fontWeight: 700 }}>
                          <TrendingUp size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 2 }} />
                          {isPositive ? '+' : ''}{improvement?.toFixed(1)} ({isPositive ? '+' : ''}{pctChange?.toFixed(1)}%)
                        </div>
                      </div>
                    </div>

                    {/* Recommendation Narrative */}
                    {scenario.result?.recommendation && (
                      <div style={{
                        marginTop: '10px', fontSize: '0.78rem', color: 'var(--color-text-secondary)',
                        lineHeight: 1.5, borderTop: '1px solid var(--color-border)',
                        paddingTop: '8px',
                      }}>
                        {scenario.result.recommendation}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default SimulationPanel;

