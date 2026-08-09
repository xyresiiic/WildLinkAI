/**
 * WildLink AI — Header Component
 */
import { TreePine, Activity, Wifi, WifiOff } from 'lucide-react';

function Header({ project, species, analysisStatus }) {
  return (
    <header className="app-header">
      <div className="logo">
        <div className="logo-icon">
          <TreePine size={18} color="white" />
        </div>
        <span>Wild<span className="highlight">Link</span> AI</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {project && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--color-text-muted)' }}>
              {project.region_name || 'Central Indian Highlands'}
            </span>
            {species && (
              <>
                <span style={{ color: 'var(--color-border)' }}>•</span>
                <span style={{ color: 'var(--color-text-secondary)' }}>
                  {species.common_name}
                </span>
              </>
            )}
          </div>
        )}

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: 'var(--radius-full)',
          background: analysisStatus === 'running'
            ? 'rgba(234, 179, 8, 0.15)'
            : analysisStatus === 'completed'
              ? 'rgba(34, 197, 94, 0.15)'
              : 'rgba(107, 143, 124, 0.15)',
          fontSize: '0.75rem',
          fontWeight: 500,
        }}>
          {analysisStatus === 'running' ? (
            <>
              <Activity size={12} style={{ color: '#eab308', animation: 'pulse 1.5s infinite' }} />
              <span style={{ color: '#eab308' }}>Analyzing</span>
            </>
          ) : analysisStatus === 'completed' ? (
            <>
              <Wifi size={12} style={{ color: '#22c55e' }} />
              <span style={{ color: '#22c55e' }}>Ready</span>
            </>
          ) : (
            <>
              <WifiOff size={12} style={{ color: 'var(--color-text-muted)' }} />
              <span style={{ color: 'var(--color-text-muted)' }}>Idle</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
