import type { Polygon } from "geojson";
import type { Place, PlaceCollection } from "../api/client";

/** Mean of a polygon's outer ring: close enough to the ward centre for "nearest place". */
export function centroid(geometry: Polygon): [number, number] {
  const ring = geometry.coordinates[0].slice(0, -1);
  const lon = ring.reduce((s, p) => s + p[0], 0) / ring.length;
  const lat = ring.reduce((s, p) => s + p[1], 0) / ring.length;
  return [lon, lat];
}

/** Great-circle distance in km. */
export function kmBetween([lon1, lat1]: [number, number], [lon2, lat2]: [number, number]): number {
  const rad = Math.PI / 180;
  const a =
    Math.sin(((lat2 - lat1) * rad) / 2) ** 2 +
    Math.cos(lat1 * rad) * Math.cos(lat2 * rad) * Math.sin(((lon2 - lon1) * rad) / 2) ** 2;
  return 6371 * 2 * Math.asin(Math.sqrt(a));
}

export interface NearPlace extends Place {
  km: number;
}

/** Places within maxKm of a point, nearest first (same 2 km walking radius as the alerts). */
export function nearestPlaces(places: PlaceCollection | null, from: [number, number], maxKm = 2, limit = 4): NearPlace[] {
  if (!places) return [];
  return places.features
    .map((f) => ({ ...f.properties, km: kmBetween(from, f.geometry.coordinates as [number, number]) }))
    .filter((p) => p.km <= maxKm)
    .sort((a, b) => a.km - b.km)
    .slice(0, limit);
}
