/**
 * WildLink AI — Header Component
 */
import { TreePine } from 'lucide-react';

function Header({ project, species, analysisStatus }) {
  const statusConfig = {
    running: { label: 'Analyzing', dotClass: 'analyzing' },
    completed: { label: 'Ready', dotClass: 'online' },
    failed: { label: 'Failed', dotClass: 'offline' },
    idle: { label: 'Idle', dotClass: 'offline' },
  };

  const { label, dotClass } = statusConfig[analysisStatus] || statusConfig.idle;

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
          padding: '5px 12px',
          borderRadius: 'var(--radius-full)',
          background: analysisStatus === 'running'
            ? 'rgba(234, 179, 8, 0.12)'
            : analysisStatus === 'completed'
              ? 'rgba(34, 197, 94, 0.12)'
              : analysisStatus === 'failed'
                ? 'rgba(239, 68, 68, 0.12)'
                : 'rgba(107, 143, 124, 0.12)',
          border: '1px solid',
          borderColor: analysisStatus === 'running'
            ? 'rgba(234, 179, 8, 0.2)'
            : analysisStatus === 'completed'
              ? 'rgba(34, 197, 94, 0.2)'
              : analysisStatus === 'failed'
                ? 'rgba(239, 68, 68, 0.2)'
                : 'rgba(107, 143, 124, 0.15)',
          fontSize: '0.75rem',
          fontWeight: 500,
          transition: 'all 0.25s ease',
        }}>
          <span className={`status-dot ${dotClass}`} />
          <span style={{
            color: analysisStatus === 'running'
              ? '#eab308'
              : analysisStatus === 'completed'
                ? '#22c55e'
                : analysisStatus === 'failed'
                  ? '#f87171'
                  : 'var(--color-text-muted)'
          }}>
            {label}
          </span>
        </div>
      </div>
    </header>
  );
}

export default Header;
