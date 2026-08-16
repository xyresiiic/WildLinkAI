/**
 * WildLink AI — Conservation Map Component
 *
 * Interactive Leaflet map with:
 * - Multi-basemap support (Dark, Satellite ESRI, Topographic)
 * - Auto-fit bounds when observations or zones load
 * - Smooth fly-to on zone selection
 * - Multi-layer toggle & opacity controls
 * - Interactive popups with action triggers
 */
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Popup, useMap } from 'react-leaflet';
import { Layers, Mountain, Globe, Moon } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

const DEFAULT_CENTER = [23.5, 80.0];
const DEFAULT_ZOOM = 7;

const BASEMAPS = {
  dark: {
    name: 'Dark Canvas',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    icon: <Moon size={14} />
  },
  satellite: {
    name: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
    icon: <Globe size={14} />
  },
  topo: {
    name: 'Terrain',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
    icon: <Mountain size={14} />
  }
};

// Auto-adjust bounds when observations/zones load
function MapBoundsController({ layers, focusCoords }) {
  const map = useMap();

  useEffect(() => {
    if (focusCoords && focusCoords.length === 2) {
      map.flyTo(focusCoords, 11, { duration: 1.5 });
      return;
    }

    const obsFeatures = layers.observations?.data?.features || [];
    const pzFeatures = layers.priority?.data?.features || [];
    const habFeatures = layers.habitat?.data?.features || [];

    const allLats = [];
    const allLngs = [];

    if (obsFeatures.length > 0) {
      obsFeatures.forEach(f => {
        if (f.geometry?.coordinates) {
          allLngs.push(f.geometry.coordinates[0]);
          allLats.push(f.geometry.coordinates[1]);
        }
      });
    } else if (pzFeatures.length > 0 || habFeatures.length > 0) {
      const src = pzFeatures.length > 0 ? pzFeatures : habFeatures.slice(0, 30);
      src.forEach(f => {
        if (f.geometry?.coordinates) {
          const ring = f.geometry.coordinates[0];
          if (Array.isArray(ring)) {
            ring.forEach(pt => {
              if (Array.isArray(pt)) {
                allLngs.push(pt[0]);
                allLats.push(pt[1]);
              }
            });
          }
        }
      });
    }

    if (allLats.length > 0 && allLngs.length > 0) {
      const minLat = Math.min(...allLats);
      const maxLat = Math.max(...allLats);
      const minLng = Math.min(...allLngs);
      const maxLng = Math.max(...allLngs);

      map.flyToBounds(
        [[minLat - 0.2, minLng - 0.2], [maxLat + 0.2, maxLng + 0.2]],
        { padding: [30, 30], duration: 1.2 }
      );
    }
  }, [layers.observations?.data, layers.priority?.data, focusCoords, map]);

  return null;
}

function ConservationMap({ layers, onZoneClick, focusCoords }) {
  const [basemapKey, setBasemapKey] = useState('dark');
  const [habitatOpacity, setHabitatOpacity] = useState(0.45);
  const [showBasemapMenu, setShowBasemapMenu] = useState(false);

  const currentBasemap = BASEMAPS[basemapKey] || BASEMAPS.dark;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={true}
        preferCanvas={true}
      >
        <MapBoundsController layers={layers} focusCoords={focusCoords} />

        {/* Tile Layer */}
        <TileLayer
          key={basemapKey}
          attribution={currentBasemap.attribution}
          url={currentBasemap.url}
          maxZoom={18}
        />

        {/* Habitat Suitability Layer */}
        {layers.habitat?.visible && layers.habitat?.data?.features && (
          <GeoJSON
            key={`habitat-${layers.habitat.data.features.length}-${habitatOpacity}`}
            data={layers.habitat.data}
            style={(feature) => habitatStyle(feature, habitatOpacity)}
            onEachFeature={(feature, layer) => {
              const props = feature.properties;
              layer.bindPopup(`
                <div style="font-family: 'Inter', sans-serif; min-width: 180px; padding: 4px 2px;">
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <strong style="color: #4ade80; font-size: 0.9rem;">🌿 Habitat Zone</strong>
                    <span style="font-size: 0.7rem; color: #a7c4b5; background: rgba(34, 197, 94, 0.15); padding: 1px 6px; border-radius: 4px;">#${props.patch_id || '?'}</span>
                  </div>
                  <div style="font-size: 0.82rem; line-height: 1.5; color: #e2e8f0;">
                    <div>Suitability: <strong style="color: #4ade80;">${(props.suitability_score * 100).toFixed(0)}%</strong></div>
                    <div>Area: ${props.area_hectares ? `${props.area_hectares.toFixed(1)} ha` : '—'}</div>
                    <div>Fragmentation: <span style="text-transform: capitalize;">${props.fragmentation_level || '—'}</span></div>
                  </div>
                </div>
              `);
            }}
          />
        )}

        {/* Corridors Layer */}
        {layers.corridors?.visible && layers.corridors?.data?.features && (
          <GeoJSON
            key={`corridors-${layers.corridors.data.features.length}`}
            data={layers.corridors.data}
            style={(feature) => corridorStyle(feature)}
            onEachFeature={(feature, layer) => {
              const props = feature.properties;
              layer.bindPopup(`
                <div style="font-family: 'Inter', sans-serif; min-width: 200px; padding: 4px 2px;">
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <strong style="color: #60a5fa; font-size: 0.9rem;">🔗 Movement Corridor</strong>
                    <span style="font-size: 0.7rem; color: #93c5fd; background: rgba(59, 130, 246, 0.15); padding: 1px 6px; border-radius: 4px;">${props.length_km ? `${props.length_km.toFixed(1)} km` : ''}</span>
                  </div>
                  <div style="font-size: 0.82rem; line-height: 1.5; color: #e2e8f0;">
                    <div>Connectivity Score: <strong style="color: #60a5fa;">${props.connectivity_score?.toFixed(1) || '—'}/100</strong></div>
                    <div>Resistance Index: ${props.resistance_score?.toFixed(1) || '—'}</div>
                    <div style="margin-top: 4px; font-size: 0.72rem; color: #94a3b8; font-style: italic;">
                      Calculated using least-cost path surface
                    </div>
                  </div>
                </div>
              `);
            }}
          />
        )}

        {/* Priority Zones Layer */}
        {layers.priority?.visible && layers.priority?.data?.features && (
          <GeoJSON
            key={`priority-${layers.priority.data.features.length}`}
            data={layers.priority.data}
            style={(feature) => priorityStyle(feature)}
            onEachFeature={(feature, layer) => {
              const props = feature.properties;
              layer.on('click', () => {
                if (onZoneClick) onZoneClick(props);
              });
              layer.bindPopup(`
                <div style="font-family: 'Inter', sans-serif; max-width: 280px; padding: 4px 2px;">
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <strong style="color: #f87171; font-size: 0.95rem;">Priority Zone #${props.rank}</strong>
                    <span style="
                      padding: 2px 7px; border-radius: 6px;
                      font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                      background: ${priorityBadgeColor(props.priority_level)};
                      color: ${priorityTextColor(props.priority_level)};
                    ">${props.priority_level}</span>
                  </div>
                  <div style="font-size: 0.82rem; line-height: 1.5; color: #cbd5e1; margin-bottom: 8px;">
                    <div>Priority Score: <strong style="color: #f87171; font-size: 0.9rem;">${props.priority_score?.toFixed(0)}/100</strong></div>
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">
                      Habitat: ${props.habitat_score?.toFixed(0)} | Conn: ${props.connectivity_score?.toFixed(0)} | Species: ${props.species_score?.toFixed(0)}
                    </div>
                  </div>
                  <div style="font-size: 0.75rem; color: #94a3b8; line-height: 1.4; margin-bottom: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px;">
                    ${props.explanation?.substring(0, 160) || ''}...
                  </div>
                </div>
              `);
            }}
          />
        )}

        {/* Observations Layer */}
        {layers.observations?.visible && layers.observations?.data?.features &&
          layers.observations.data.features.map((feature, idx) => (
            <CircleMarker
              key={`obs-${idx}`}
              center={[
                feature.geometry.coordinates[1],
                feature.geometry.coordinates[0]
              ]}
              radius={5}
              pathOptions={{
                color: '#f59e0b',
                fillColor: '#fbbf24',
                fillOpacity: 0.85,
                weight: 1.5,
              }}
            >
              <Popup>
                <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.82rem', minWidth: '160px' }}>
                  <div style={{ fontWeight: 700, color: '#fbbf24', marginBottom: 4 }}>📍 Species Observation</div>
                  <div>Source: {feature.properties.source || 'Field Survey'}</div>
                  <div>Date: {feature.properties.observed_at ? new Date(feature.properties.observed_at).toLocaleDateString() : 'Recorded'}</div>
                  <div>Confidence: {feature.properties.confidence ? `${(feature.properties.confidence * 100).toFixed(0)}%` : 'Verified'}</div>
                </div>
              </Popup>
            </CircleMarker>
          ))
        }
      </MapContainer>

      {/* Floating Basemap & GIS Controls Toolbar */}
      <div style={{
        position: 'absolute', top: 16, right: 16, zIndex: 1000,
        display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end',
      }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {/* Zoom to Landscape Fit Button */}
          <button
            onClick={() => {
              const obsFeatures = layers.observations?.data?.features || [];
              const pzFeatures = layers.priority?.data?.features || [];
              const habFeatures = layers.habitat?.data?.features || [];
              const allLats = [];
              const allLngs = [];

              if (obsFeatures.length > 0) {
                obsFeatures.forEach(f => {
                  if (f.geometry?.coordinates) {
                    allLngs.push(f.geometry.coordinates[0]);
                    allLats.push(f.geometry.coordinates[1]);
                  }
                });
              } else if (pzFeatures.length > 0 || habFeatures.length > 0) {
                const src = pzFeatures.length > 0 ? pzFeatures : habFeatures.slice(0, 30);
                src.forEach(f => {
                  if (f.geometry?.coordinates) {
                    const ring = f.geometry.coordinates[0];
                    if (Array.isArray(ring)) {
                      ring.forEach(pt => {
                        if (Array.isArray(pt)) {
                          allLngs.push(pt[0]);
                          allLats.push(pt[1]);
                        }
                      });
                    }
                  }
                });
              }

              if (allLats.length > 0 && allLngs.length > 0) {
                const minLat = Math.min(...allLats);
                const maxLat = Math.max(...allLats);
                const minLng = Math.min(...allLngs);
                const maxLng = Math.max(...allLngs);
                const mapEl = document.querySelector('.leaflet-container');
                if (mapEl && mapEl._leaflet_map) {
                  mapEl._leaflet_map.flyToBounds(
                    [[minLat - 0.2, minLng - 0.2], [maxLat + 0.2, maxLng + 0.2]],
                    { padding: [30, 30], duration: 1.2 }
                  );
                }
              }
            }}
            className="btn btn-secondary btn-sm"
            style={{
              background: 'rgba(17, 26, 22, 0.85)',
              backdropFilter: 'blur(12px)',
              border: '1px solid var(--color-border)',
              display: 'flex', alignItems: 'center', gap: 6,
              boxShadow: 'var(--shadow-md)',
            }}
            title="Reset view to whole study area"
          >
            <Mountain size={14} color="var(--color-primary-light)" />
            <span style={{ fontSize: '0.78rem' }}>Fit Study Area</span>
          </button>

          {/* Basemap Switcher Button */}
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setShowBasemapMenu(prev => !prev)}
              className="btn btn-secondary btn-sm"
              style={{
                background: 'rgba(17, 26, 22, 0.85)',
                backdropFilter: 'blur(12px)',
                border: '1px solid var(--color-border)',
                display: 'flex', alignItems: 'center', gap: 6,
                boxShadow: 'var(--shadow-md)',
              }}
              title="Switch Basemap Style"
            >
              <Layers size={14} color="var(--color-primary-light)" />
              <span style={{ fontSize: '0.78rem' }}>{currentBasemap.name}</span>
            </button>

            {showBasemapMenu && (
              <div style={{
                position: 'absolute', top: '100%', right: 0, marginTop: 6,
                background: 'var(--color-bg-secondary)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: 6, display: 'flex', flexDirection: 'column', gap: 4,
                minWidth: 150, boxShadow: 'var(--shadow-lg)',
                zIndex: 1100,
              }}>
                {Object.entries(BASEMAPS).map(([key, config]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setBasemapKey(key);
                      setShowBasemapMenu(false);
                    }}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 8,
                      padding: '6px 10px', borderRadius: 'var(--radius-sm)',
                      background: basemapKey === key ? 'var(--color-primary-glow)' : 'transparent',
                      border: 'none', color: basemapKey === key ? 'var(--color-primary-light)' : 'var(--color-text-secondary)',
                      cursor: 'pointer', fontSize: '0.78rem', textAlign: 'left',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {config.icon}
                    <span>{config.name}</span>
                    {basemapKey === key && <span style={{ marginLeft: 'auto', fontSize: '0.65rem' }}>✓</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Habitat Opacity Quick Slider */}
        {layers.habitat?.visible && (
          <div style={{
            background: 'rgba(17, 26, 22, 0.85)',
            backdropFilter: 'blur(12px)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            padding: '6px 10px', display: 'flex', alignItems: 'center', gap: 8,
            boxShadow: 'var(--shadow-md)', fontSize: '0.72rem', color: 'var(--color-text-muted)',
          }}>
            <span>🌿 Opacity:</span>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.05"
              value={habitatOpacity}
              onChange={(e) => setHabitatOpacity(parseFloat(e.target.value))}
              style={{ width: 70, cursor: 'pointer', accentColor: 'var(--color-primary)' }}
            />
          </div>
        )}
      </div>

      {/* Floating Layer Feature Counters HUD at Bottom Right */}
      <div style={{
        position: 'absolute', bottom: 16, right: 16, zIndex: 1000,
        display: 'flex', gap: 6, alignItems: 'center',
        background: 'rgba(17, 26, 22, 0.85)',
        backdropFilter: 'blur(12px)',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius-full)',
        padding: '4px 10px',
        boxShadow: 'var(--shadow-md)',
        fontSize: '0.72rem',
        color: 'var(--color-text-secondary)',
      }}>
        {layers.observations?.data?.features?.length > 0 && (
          <span style={{ color: '#fbbf24' }}>
            📍 {layers.observations.data.features.length} Obs
          </span>
        )}
        {layers.corridors?.data?.features?.length > 0 && (
          <span style={{ color: '#60a5fa', borderLeft: '1px solid rgba(255,255,255,0.15)', paddingLeft: 6 }}>
            🔗 {layers.corridors.data.features.length} Corridors
          </span>
        )}
        {layers.priority?.data?.features?.length > 0 && (
          <span style={{ color: '#f87171', borderLeft: '1px solid rgba(255,255,255,0.15)', paddingLeft: 6 }}>
            🎯 {layers.priority.data.features.length} Priority Zones
          </span>
        )}
      </div>
    </div>
  );
}

// ────────────── Style Functions ──────────────

function habitatStyle(feature, opacity = 0.45) {
  const score = feature.properties.suitability_score || 0;
  return {
    fillColor: suitabilityColor(score),
    fillOpacity: opacity,
    color: suitabilityColor(score),
    weight: 0.4,
    opacity: Math.min(1.0, opacity + 0.2),
  };
}

function corridorStyle(feature) {
  const score = feature.properties.connectivity_score || 50;
  const width = Math.max(2.5, Math.min(6, score / 16));
  return {
    color: '#60a5fa',
    weight: width,
    opacity: 0.85,
    dashArray: score > 75 ? null : '6 4',
  };
}

function priorityStyle(feature) {
  const level = feature.properties.priority_level;
  const colors = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e',
  };
  return {
    fillColor: colors[level] || '#eab308',
    fillOpacity: 0.32,
    color: colors[level] || '#eab308',
    weight: 2.2,
    opacity: 0.9,
    dashArray: '5 3',
  };
}

function suitabilityColor(score) {
  if (score >= 0.8) return '#15803d';
  if (score >= 0.6) return '#22c55e';
  if (score >= 0.4) return '#eab308';
  if (score >= 0.2) return '#f97316';
  return '#ef4444';
}

function priorityBadgeColor(level) {
  const colors = {
    critical: 'rgba(239, 68, 68, 0.25)',
    high: 'rgba(249, 115, 22, 0.25)',
    medium: 'rgba(234, 179, 8, 0.25)',
    low: 'rgba(34, 197, 94, 0.25)',
  };
  return colors[level] || colors.medium;
}

function priorityTextColor(level) {
  const colors = {
    critical: '#f87171',
    high: '#fb923c',
    medium: '#fbbf24',
    low: '#4ade80',
  };
  return colors[level] || colors.medium;
}

export default ConservationMap;

