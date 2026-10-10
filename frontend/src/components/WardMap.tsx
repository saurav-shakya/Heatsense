import type { FeatureCollection } from "geojson";
import * as maplibregl from "maplibre-gl";
import type { GeoJSONSource, MapLayerMouseEvent } from "maplibre-gl";
import { useEffect, useRef } from "react";
import type { WardCollection } from "../api/client";
import type { Strings } from "../i18n/strings";

// Free vector basemap, no API key. Positron is near-monochrome so the risk fills carry the colour.
const BASEMAP = "https://tiles.openfreemap.org/styles/positron";

const css = (name: string) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

interface Props {
  data: WardCollection;
  day: number;
  selected: string | null;
  onSelect: (wardId: string) => void;
  t: Strings;
}

/** Flatten the chosen day's level onto each feature so one `match` expression can colour it. */
function forDay(data: WardCollection, day: number): FeatureCollection {
  return {
    type: "FeatureCollection",
    features: data.features.map((f) => ({
      type: "Feature",
      id: f.id,
      geometry: f.geometry,
      properties: { wardId: f.id, name: f.properties.name, level: f.properties.daily?.[day]?.level ?? "low" },
    })),
  };
}

function bounds(data: WardCollection): maplibregl.LngLatBoundsLike {
  const b = new maplibregl.LngLatBounds();
  for (const f of data.features) for (const [lon, lat] of f.geometry.coordinates[0]) b.extend([lon, lat]);
  return b;
}

export default function WardMap({ data, day, selected, onSelect, t }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const ready = useRef(false);
  const prevSelected = useRef<string | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    const m = new maplibregl.Map({
      container: container.current!,
      style: BASEMAP,
      bounds: bounds(data),
      fitBoundsOptions: { padding: 24 },
      attributionControl: { compact: true },
      dragRotate: false,
      pitchWithRotate: false,
    });
    m.touchZoomRotate.disableRotation();
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.current = m;

    // style.load fires once the style JSON is parsed, before basemap tiles arrive, so wards draw immediately.
    m.once("style.load", () => {
      if (m.getLayer("background")) m.setPaintProperty("background", "background-color", css("--sheet"));
      // Keep basemap place names readable on top of the ward fills.
      const firstLabel = m.getStyle().layers.find((l) => l.type === "symbol")?.id;
      m.resize();
      m.fitBounds(bounds(data), { padding: 24, duration: 0 });
      m.addSource("wards", { type: "geojson", data: forDay(data, day), promoteId: "wardId" });
      m.addLayer({
        id: "ward-fill",
        type: "fill",
        source: "wards",
        paint: {
          "fill-color": [
            "match",
            ["get", "level"],
            "extreme", css("--risk-extreme"),
            "high", css("--risk-high"),
            "moderate", css("--risk-moderate"),
            css("--risk-low"),
          ],
          "fill-opacity": 0.82,
        },
      }, firstLabel);
      m.addLayer({
        id: "ward-edge",
        type: "line",
        source: "wards",
        paint: { "line-color": css("--sheet"), "line-width": 0.6 },
      }, firstLabel);
      m.addLayer({
        id: "ward-selected",
        type: "line",
        source: "wards",
        paint: {
          "line-color": css("--indigo"),
          "line-width": ["case", ["boolean", ["feature-state", "selected"], false], 3, 0],
        },
      });
      ready.current = true;
    });

    m.on("click", "ward-fill", (e: MapLayerMouseEvent) => {
      const id = e.features?.[0]?.properties?.wardId;
      if (id) onSelectRef.current(id);
    });
    m.on("mouseenter", "ward-fill", () => (m.getCanvas().style.cursor = "pointer"));
    m.on("mouseleave", "ward-fill", () => (m.getCanvas().style.cursor = ""));

    return () => {
      ready.current = false;
      m.remove();
    };
    // The map is created once; data/day updates go through setData below.
  }, []);

  useEffect(() => {
    const m = map.current;
    if (!m || !ready.current) return;
    (m.getSource("wards") as GeoJSONSource | undefined)?.setData(forDay(data, day));
  }, [data, day]);

  useEffect(() => {
    const m = map.current;
    if (!m) return;
    const apply = () => {
      if (prevSelected.current) m.setFeatureState({ source: "wards", id: prevSelected.current }, { selected: false });
      if (selected) {
        m.setFeatureState({ source: "wards", id: selected }, { selected: true });
        const f = data.features.find((x) => x.id === selected);
        if (f) m.fitBounds(bounds({ ...data, features: [f] }), { padding: 80, maxZoom: 11.5, duration: 600 });
      }
      prevSelected.current = selected;
    };
    if (ready.current) apply();
    else m.once("idle", apply);
  }, [selected, data]);

  return <div ref={container} className="map" role="region" aria-label={t.legend} />;
}
