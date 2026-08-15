/**
 * WildLink AI — Conservation Map Component
 *
 * Interactive Leaflet map with multi-layer support for:
 * - Species observations (markers)
 * - Habitat suitability (colored polygons)
 * - Connectivity corridors (polylines)
 * - Priority zones (highlighted polygons)
 */
import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Central Indian Highlands center
const DEFAULT_CENTER = [23.5, 80.0];
const DEFAULT_ZOOM = 7;

function ConservationMap({ layers, onZoneClick }) {
  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      style={{ width: '100%', height: '100%' }}
      zoomControl={true}
      preferCanvas={true}
    >
      {/* Dark tile layer */}
      <TileLayer
        attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />

      {/* Habitat Suitability Layer */}
      {layers.habitat?.visible && layers.habitat?.data?.features && (
        <GeoJSON
          key={`habitat-${layers.habitat.data.features.length}`}
          data={layers.habitat.data}
          style={(feature) => habitatStyle(feature)}
          onEachFeature={(feature, layer) => {
            const props = feature.properties;
            layer.bindPopup(`
              <div style="font-family: Inter, sans-serif;">
                <strong style="color: #4ade80;">Habitat Zone</strong><br/>
                <div style="margin-top: 6px; font-size: 0.85rem;">
                  Suitability: <strong>${(props.suitability_score * 100).toFixed(0)}%</strong><br/>
                  Area: ${props.area_hectares?.toFixed(1) || '—'} ha<br/>
                  Fragmentation: ${props.fragmentation_level || '—'}
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
              <div style="font-family: Inter, sans-serif;">
                <strong style="color: #60a5fa;">Potential Corridor</strong><br/>
                <div style="margin-top: 6px; font-size: 0.85rem;">
                  Connectivity: <strong>${props.connectivity_score?.toFixed(1) || '—'}/100</strong><br/>
                  Length: ${props.length_km?.toFixed(1) || '—'} km<br/>
                  Patches: ${props.source_patch_id} → ${props.target_patch_id}
                </div>
                <div style="margin-top: 4px; font-size: 0.75rem; color: #a7c4b5; font-style: italic;">
                  Potential connectivity corridor under current model assumptions
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
              <div style="font-family: Inter, sans-serif; max-width: 280px;">
                <strong style="color: #f87171;">Priority Zone #${props.rank}</strong>
                <span style="
                  margin-left: 8px; padding: 1px 6px; border-radius: 8px;
                  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
                  background: ${priorityBadgeColor(props.priority_level)};
                  color: ${priorityTextColor(props.priority_level)};
                ">${props.priority_level}</span>
                <div style="margin-top: 8px; font-size: 0.85rem;">
                  Score: <strong>${props.priority_score?.toFixed(0)}/100</strong><br/>
                  Habitat: ${props.habitat_score?.toFixed(0)} | 
                  Connectivity: ${props.connectivity_score?.toFixed(0)} | 
                  Species: ${props.species_score?.toFixed(0)}<br/>
                  Evidence: ${props.evidence_quality || 'moderate'}
                </div>
                <div style="margin-top: 6px; font-size: 0.8rem; color: #a7c4b5; line-height: 1.4;">
                  ${props.explanation?.substring(0, 200) || ''}
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
              fillOpacity: 0.7,
              weight: 1.5,
            }}
          >
            <Popup>
              <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '0.85rem' }}>
                <strong style={{ color: '#fbbf24' }}>Species Observation</strong><br/>
                Source: {feature.properties.source || 'Unknown'}<br/>
                Date: {feature.properties.observed_at || 'Unknown'}<br/>
                Confidence: {feature.properties.confidence ? 
                  `${(feature.properties.confidence * 100).toFixed(0)}%` : '—'}
                <div style={{ marginTop: '4px', fontSize: '0.75rem', color: '#a7c4b5', fontStyle: 'italic' }}>
                  Observed data point
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))
      }
    </MapContainer>
  );
}

// ────────────── Style Functions ──────────────

function habitatStyle(feature) {
  const score = feature.properties.suitability_score || 0;
  return {
    fillColor: suitabilityColor(score),
    fillOpacity: 0.45,
    color: suitabilityColor(score),
    weight: 0.3,
    opacity: 0.6,
  };
}

function corridorStyle(feature) {
  const score = feature.properties.connectivity_score || 50;
  const width = Math.max(2, Math.min(5, score / 20));
  return {
    color: '#60a5fa',
    weight: width,
    opacity: 0.7,
    dashArray: score > 70 ? null : '8 4',
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
    fillOpacity: 0.25,
    color: colors[level] || '#eab308',
    weight: 2,
    opacity: 0.8,
    dashArray: '4 2',
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
    critical: 'rgba(239, 68, 68, 0.2)',
    high: 'rgba(249, 115, 22, 0.2)',
    medium: 'rgba(234, 179, 8, 0.2)',
    low: 'rgba(34, 197, 94, 0.2)',
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
