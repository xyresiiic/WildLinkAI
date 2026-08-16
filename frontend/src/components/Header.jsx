/**
 * WildLink AI — Header Component
 */
import { useState } from 'react';
import { TreePine, Download, PlusCircle, FolderOpen, ChevronDown } from 'lucide-react';

function Header({
  project,
  species,
  analysisStatus,
  projectsList = [],
  onSelectProject,
  onNewAnalysis,
  onExportData,
}) {
  const [showProjectsMenu, setShowProjectsMenu] = useState(false);

  const statusConfig = {
    running: { label: 'Analyzing', dotClass: 'analyzing' },
    completed: { label: 'Ready', dotClass: 'online' },
    failed: { label: 'Failed', dotClass: 'offline' },
    idle: { label: 'Idle', dotClass: 'offline' },
  };

  const { label, dotClass } = statusConfig[analysisStatus] || statusConfig.idle;

  return (
    <header className="app-header">
      {/* Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div className="logo" style={{ cursor: 'pointer' }} onClick={onNewAnalysis}>
          <div className="logo-icon">
            <TreePine size={18} color="white" />
          </div>
          <span>Wild<span className="highlight">Link</span> AI</span>
        </div>

        {/* Project Selector Dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setShowProjectsMenu(prev => !prev)}
            className="btn btn-secondary btn-sm"
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'var(--color-bg-card)',
              fontSize: '0.8rem',
            }}
          >
            <FolderOpen size={14} color="var(--color-primary-light)" />
            <span style={{ maxWidth: 160, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {project ? project.name : 'Select Project'}
            </span>
            <ChevronDown size={13} style={{ opacity: 0.6 }} />
          </button>

          {showProjectsMenu && (
            <div style={{
              position: 'absolute', top: '100%', left: 0, marginTop: 6,
              background: 'var(--color-bg-secondary)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              padding: 6, display: 'flex', flexDirection: 'column', gap: 4,
              minWidth: 260, maxHeight: 320, overflowY: 'auto',
              boxShadow: 'var(--shadow-lg)', zIndex: 1200,
            }}>
              <div style={{ padding: '6px 8px', fontSize: '0.72rem', color: 'var(--color-text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Existing Projects ({projectsList.length})
              </div>

              {projectsList.length === 0 ? (
                <div style={{ padding: '8px 10px', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                  No saved projects yet.
                </div>
              ) : (
                projectsList.map(p => (
                  <button
                    key={p.id}
                    onClick={() => {
                      if (onSelectProject) onSelectProject(p.id);
                      setShowProjectsMenu(false);
                    }}
                    style={{
                      display: 'flex', flexDirection: 'column', alignItems: 'flex-start',
                      padding: '8px 10px', borderRadius: 'var(--radius-sm)',
                      background: project?.id === p.id ? 'var(--color-primary-glow)' : 'transparent',
                      border: 'none', color: project?.id === p.id ? 'var(--color-primary-light)' : 'var(--color-text-primary)',
                      cursor: 'pointer', textAlign: 'left',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{p.name}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                      {p.species?.common_name || 'Species'} • {p.region_name || 'Region'}
                    </div>
                  </button>
                ))
              )}

              <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 4, marginTop: 4 }}>
                <button
                  onClick={() => {
                    if (onNewAnalysis) onNewAnalysis();
                    setShowProjectsMenu(false);
                  }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 6, width: '100%',
                    padding: '8px 10px', borderRadius: 'var(--radius-sm)',
                    background: 'var(--color-primary-glow)',
                    border: 'none', color: 'var(--color-primary-light)',
                    cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
                  }}
                >
                  <PlusCircle size={14} />
                  <span>New Conservation Analysis</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Center/Right Section */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {project && (
          <>
            <button
              onClick={onNewAnalysis}
              className="btn btn-secondary btn-sm"
              title="Start a new analysis for another species"
            >
              <PlusCircle size={14} />
              <span>New Analysis</span>
            </button>

            <button
              onClick={onExportData}
              className="btn btn-secondary btn-sm"
              title="Export GeoJSON layers and conservation summary"
            >
              <Download size={14} />
              <span>Export Report</span>
            </button>
          </>
        )}

        {/* Status Pill */}
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

