/**
 * WildLink AI — Zone Detail Modal
 */
import { X, Target, BarChart3, Shield, TreePine, Zap, Sparkles, CheckCircle2 } from 'lucide-react';

function ZoneDetailModal({ zone, onClose, onSimulate }) {
  if (!zone) return null;

  const factors = [
    { key: 'habitat_score', label: 'Habitat Suitability', icon: <TreePine size={14} />, color: '#22c55e' },
    { key: 'connectivity_score', label: 'Connectivity Potential', icon: <Zap size={14} />, color: '#3b82f6' },
    { key: 'species_score', label: 'Species Relevance', icon: <Target size={14} />, color: '#f59e0b' },
    { key: 'restoration_score', label: 'Restoration Feasibility', icon: <Shield size={14} />, color: '#8b5cf6' },
  ];

  const recommendedAction = zone.recommended_action || (
    zone.dominant_factor === 'connectivity'
      ? 'Construct Wildlife Overpass / Eco-duct across Transport Corridor'
      : zone.dominant_factor === 'restoration'
        ? 'Targeted Reforestation & Native Vegetation Corridor Planting'
        : 'Designate Protected Core Buffer & Enhance Anti-Poaching Patrols'
  );

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(6px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 2000, padding: '20px',
    }} onClick={onClose}>
      <div
        className="card animate-fade-in"
        style={{
          maxWidth: '520px', width: '100%',
          background: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-lg)',
          maxHeight: '90vh', overflowY: 'auto',
          boxShadow: 'var(--shadow-lg)',
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          marginBottom: '16px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                fontFamily: 'var(--font-display)', fontWeight: 800,
                fontSize: '1.6rem', color: 'var(--color-text-accent)'
              }}>
                #{zone.rank || '?'}
              </span>
              <span className={`badge badge-${zone.priority_level || 'medium'}`} style={{ textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                {zone.priority_level || 'medium'} Priority
              </span>
            </div>
            <div style={{
              fontFamily: 'var(--font-display)', fontWeight: 600,
              fontSize: '1.1rem', marginTop: '2px'
            }}>
              Conservation Priority Zone
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--color-text-muted)', padding: '4px',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Score Card & Action */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px',
          marginBottom: '16px',
        }}>
          <div style={{
            textAlign: 'center', padding: '14px',
            background: 'var(--color-bg-glass)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            display: 'flex', flexDirection: 'column', justifyContent: 'center',
          }}>
            <div style={{
              fontFamily: 'var(--font-display)', fontWeight: 800,
              fontSize: '2.4rem', lineHeight: 1,
              background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-accent-teal))',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}>
              {zone.priority_score?.toFixed(0) || '—'}
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', marginTop: '4px', fontWeight: 600 }}>
              PRIORITY SCORE / 100
            </div>
          </div>

          <div style={{
            padding: '12px 14px',
            background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(20, 184, 166, 0.05))',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '4px',
          }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--color-primary-light)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
              <Sparkles size={12} /> RECOMMENDED ACTION
            </div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-primary)', lineHeight: 1.4 }}>
              {recommendedAction}
            </div>
          </div>
        </div>

        {/* Factor Breakdown */}
        <div className="section-header">
          <span className="section-title">Ecological Multi-Criteria Scoring</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
          {factors.map(({ key, label, icon, color }) => {
            const value = zone[key] || 0;
            return (
              <div key={key}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  fontSize: '0.82rem', marginBottom: '4px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-text-secondary)' }}>
                    {icon} {label}
                    {zone.dominant_factor === key.replace('_score', '') && (
                      <span style={{
                        fontSize: '0.65rem', background: 'rgba(34, 197, 94, 0.15)',
                        color: '#4ade80', padding: '1px 5px', borderRadius: '4px', fontWeight: 700,
                      }}>KEY DRIVER</span>
                    )}
                  </div>
                  <span style={{ fontWeight: 700 }}>{value.toFixed(0)}</span>
                </div>
                <div className="score-bar">
                  <div className="score-bar-fill" style={{
                    width: `${Math.min(100, Math.max(0, value))}%`,
                    background: color,
                  }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Evidence & Metrics */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px',
          padding: '10px 12px', background: 'var(--color-bg-card)',
          borderRadius: 'var(--radius-md)', marginBottom: '16px', fontSize: '0.8rem',
        }}>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Evidence Quality: </span>
            <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{zone.evidence_quality || 'Moderate'}</span>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Zone Footprint: </span>
            <span style={{ fontWeight: 600 }}>{zone.area_hectares ? `${zone.area_hectares.toFixed(1)} ha` : 'Regional'}</span>
          </div>
        </div>

        {/* Explainability Summary */}
        <div className="section-header">
          <span className="section-title">Explainable Intelligence</span>
        </div>
        <p style={{
          fontSize: '0.84rem', lineHeight: 1.6, color: 'var(--color-text-secondary)',
          marginBottom: '20px',
        }}>
          {zone.explanation || 'Calculated using spatial habitat density, least-cost connectivity benefits, and restoration potential.'}
        </p>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-primary" style={{ flex: 1 }} onClick={onSimulate}>
            <BarChart3 size={15} />
            Simulate Restoration in What-If
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default ZoneDetailModal;

