/**
 * WildLink AI — What-If Simulation Panel
 */
import { useState, useEffect } from 'react';
import { X, Play, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';
import { createSimulation, getProjectSimulations, getSimulation } from '../services/api';

function SimulationPanel({ project, priorityZones, onClose }) {
  const [selectedZones, setSelectedZones] = useState([]);
  const [scenarioName, setScenarioName] = useState('');
  const [simulating, setSimulating] = useState(false);
  const [scenarios, setScenarios] = useState([]);
  const [baseline, setBaseline] = useState(null);

  // Load existing simulations
  useEffect(() => {
    loadScenarios();
  }, [project.id]);

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

  const handleSimulate = async () => {
    if (selectedZones.length === 0 && !scenarioName) return;

    setSimulating(true);
    try {
      const res = await createSimulation({
        project_id: project.id,
        name: scenarioName || `Scenario ${scenarios.length + 1}`,
        intervention_type: 'habitat_restoration',
        zone_ids: selectedZones.length > 0 ? selectedZones : undefined,
      });

      const simId = res.data.data?.id;
      if (simId) {
        // Poll until complete
        await pollSimulation(simId);
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
      }, 1500);
    });
  };

  return (
    <div style={{
      position: 'fixed', top: 0, right: 0, bottom: 0,
      width: '420px', background: 'var(--color-bg-secondary)',
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
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.1rem' }}>
            🔬 What-If Simulator
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            Compare restoration scenarios
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
        {/* Disclaimer */}
        <div style={{
          background: 'rgba(234, 179, 8, 0.08)', border: '1px solid rgba(234, 179, 8, 0.2)',
          borderRadius: 'var(--radius-md)', padding: '10px 12px',
          fontSize: '0.75rem', color: 'var(--color-accent-amber)',
          display: 'flex', gap: '8px', alignItems: 'start',
          marginBottom: '16px',
        }}>
          <AlertTriangle size={14} style={{ flexShrink: 0, marginTop: '1px' }} />
          <span>Simulation results are model-based estimates under current assumptions, not guaranteed ecological outcomes.</span>
        </div>

        {/* Create Scenario */}
        <div className="section-header">
          <span className="section-title">Create Scenario</span>
        </div>

        <div className="form-group">
          <label className="form-label">Scenario Name</label>
          <input
            type="text"
            className="form-input"
            placeholder="e.g., Restore Priority Zone #1"
            value={scenarioName}
            onChange={(e) => setScenarioName(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Select Zones to Restore</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '180px', overflowY: 'auto' }}>
            {priorityZones.slice(0, 10).map((zone, idx) => (
              <label
                key={zone.id || idx}
                className="layer-toggle"
                style={{
                  background: selectedZones.includes(zone.id)
                    ? 'var(--color-primary-glow)' : 'var(--color-bg-glass)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid',
                  borderColor: selectedZones.includes(zone.id)
                    ? 'var(--color-primary)' : 'var(--color-border)',
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedZones.includes(zone.id)}
                  onChange={() => toggleZone(zone.id)}
                />
                <span style={{ fontSize: '0.82rem' }}>
                  #{zone.rank || idx + 1} — Score: {zone.priority_score?.toFixed(0)}
                </span>
                <span className={`badge badge-${zone.priority_level}`} style={{ marginLeft: 'auto' }}>
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
            <><span className="animate-pulse">⏳</span> Simulating...</>
          ) : (
            <><Play size={14} /> Run Simulation</>
          )}
        </button>

        {/* Scenario Comparison */}
        {scenarios.length > 0 && (
          <>
            <div className="section-header">
              <span className="section-title">Scenario Comparison</span>
            </div>

            {/* Baseline */}
            {baseline !== null && (
              <div className="scenario-card" style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>BASELINE</div>
                    <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '0.95rem' }}>
                      Current Connectivity
                    </div>
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-display)', fontWeight: 700,
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
                  <div key={scenario.id || idx} className="scenario-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                          Scenario {idx + 1}
                        </div>
                        <div style={{ fontFamily: 'var(--font-display)', fontWeight: 600, fontSize: '0.9rem' }}>
                          {scenario.name}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{
                          fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1.3rem',
                          color: 'var(--color-text-primary)'
                        }}>
                          {scenario.simulated_connectivity?.toFixed(1)}
                        </div>
                        <div className={`scenario-delta ${isPositive ? 'positive' : 'negative'}`}
                          style={{ fontSize: '0.9rem' }}>
                          <TrendingUp size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
                          {isPositive ? '+' : ''}{improvement?.toFixed(1)} ({pctChange?.toFixed(1)}%)
                        </div>
                      </div>
                    </div>

                    {/* Recommendation */}
                    {scenario.result?.recommendation && (
                      <div style={{
                        marginTop: '10px', fontSize: '0.8rem', color: 'var(--color-text-muted)',
                        lineHeight: 1.5, borderTop: '1px solid var(--color-border)',
                        paddingTop: '10px',
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
