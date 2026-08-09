/**
 * WildLink AI — Zone Detail Modal
 */
import { X, Target, BarChart3, Shield, TreePine, Zap } from 'lucide-react';

function ZoneDetailModal({ zone, onClose, onSimulate }) {
  if (!zone) return null;

  const factors = [
    { key: 'habitat_score', label: 'Habitat Value', icon: <TreePine size={14} />, color: '#22c55e' },
    { key: 'connectivity_score', label: 'Connectivity Benefit', icon: <Zap size={14} />, color: '#3b82f6' },
    { key: 'species_score', label: 'Species Relevance', icon: <Target size={14} />, color: '#f59e0b' },
    { key: 'restoration_score', label: 'Restoration Opportunity', icon: <Shield size={14} />, color: '#8b5cf6' },
  ];

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 2000, padding: '20px',
    }} onClick={onClose}>
      <div
        className="card animate-fade-in"
        style={{
          maxWidth: '480px', width: '100%',
          background: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'start',
          marginBottom: '20px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{
                fontFamily: 'var(--font-display)', fontWeight: 800,
                fontSize: '1.5rem', color: 'var(--color-text-accent)'
              }}>
                #{zone.rank || '?'}
              </span>
              <span className={`badge badge-${zone.priority_level || 'medium'}`}>
                {zone.priority_level || 'medium'}
              </span>
            </div>
            <div style={{
              fontFamily: 'var(--font-display)', fontWeight: 600,
              fontSize: '1.1rem', marginTop: '4px'
            }}>
              Priority Zone
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

        {/* Score */}
        <div style={{
          textAlign: 'center', padding: '16px',
          background: 'var(--color-bg-glass)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '16px',
        }}>
          <div style={{
            fontFamily: 'var(--font-display)', fontWeight: 800,
            fontSize: '2.5rem', lineHeight: 1,
            background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-accent-teal))',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
            {zone.priority_score?.toFixed(0) || '—'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>
            PRIORITY SCORE / 100
          </div>
        </div>

        {/* Factor Breakdown */}
        <div className="section-header">
          <span className="section-title">Factor Breakdown</span>
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
                        color: '#4ade80', padding: '1px 5px', borderRadius: '4px'
                      }}>DOMINANT</span>
                    )}
                  </div>
                  <span style={{ fontWeight: 600 }}>{value.toFixed(0)}</span>
                </div>
                <div className="score-bar">
                  <div className="score-bar-fill" style={{
                    width: `${Math.min(100, value)}%`,
                    background: color,
                  }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* Evidence Quality */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <span style={{ fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>Evidence Quality</span>
          <span className={`badge badge-evidence-${zone.evidence_quality || 'moderate'}`}>
            {zone.evidence_quality || 'moderate'}
          </span>
        </div>

        {/* Explanation */}
        <div className="section-header">
          <span className="section-title">Explanation</span>
        </div>
        <p style={{
          fontSize: '0.85rem', lineHeight: 1.6, color: 'var(--color-text-secondary)',
          marginBottom: '20px',
        }}>
          {zone.explanation || 'No explanation available.'}
        </p>

        {/* Area */}
        {zone.area_hectares && (
          <div style={{
            fontSize: '0.8rem', color: 'var(--color-text-muted)',
            marginBottom: '16px'
          }}>
            Area: {zone.area_hectares.toFixed(1)} hectares
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-primary" style={{ flex: 1 }} onClick={onSimulate}>
            <BarChart3 size={14} />
            Simulate Restoration
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
