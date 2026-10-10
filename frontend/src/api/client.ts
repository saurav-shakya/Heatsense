// Typed client for the HeatShield HTTP API (backend/functions/api/app.py).

import type { Point, Polygon } from "geojson";

export type RiskLevel = "low" | "moderate" | "high" | "extreme";
export const LEVELS: RiskLevel[] = ["low", "moderate", "high", "extreme"];

/** Daytime IST hours [from, to) when outdoor work must be cut to `work` minutes an hour (0 = stop). */
export interface WorkSegment {
  from: number;
  to: number;
  work: number;
}

/** What the ward office should do; strings.ts turns each code into a sentence. */
export type ActionCode = "open_cooling" | "shift_work" | "check_vulnerable" | "night_shelter" | "cooling_gap";

export interface DailyRisk {
  date: string; // IST calendar date, YYYY-MM-DD
  risk: number; // 0..1
  level: RiskLevel;
  heatIndex: number; // deg C at the peak hour
  peakAt: string; // UTC ISO of the peak hour
  // Added with the body-heat model; missing from snapshots made before it.
  wbgtMax?: number; // deg C, estimated WBGT in full sun at the day's worst hour
  workPlan?: WorkSegment[];
  nightMin?: number; // deg C, tonight's low in the ward
  hotNight?: boolean;
  actions?: ActionCode[];
}

export interface WardProps {
  wardId: string;
  name: string;
  lstOffset: number;
  ndvi: number;
  popDensity: number;
  vulnerabilityScore: number;
  daily: DailyRisk[] | null;
  fixture?: boolean; // true for the synthetic placeholder grid
}

export interface WardCollection {
  type: "FeatureCollection";
  city: string;
  replayOf: string | null; // set while scores replay a past heatwave (YYYY-MM-DD)
  snapshotAt?: string; // UTC ISO; set when the data is the saved snapshot, not the live API
  features: Array<{
    type: "Feature";
    id: string;
    geometry: Polygon;
    properties: WardProps;
  }>;
}

export interface HourlyRisk {
  forecastTime: string;
  heatIndex: number;
  hazard: number;
  risk: number;
  level: RiskLevel;
  airTemp?: number;
  wbgt?: number;
}

export type PlaceKind = "cooling" | "water" | "rest";

export interface Place {
  id: string;
  name: string;
  nameHi?: string;
  kind: PlaceKind;
  hours?: [number, number]; // IST [open, close); missing = always open
  verified: boolean; // false = sample point, never used in alerts
}

export interface PlaceCollection {
  type: "FeatureCollection";
  features: Array<{ type: "Feature"; id: string; geometry: Point; properties: Place }>;
}

export interface WardForecast {
  ward: WardProps;
  hourly: HourlyRisk[];
}

export type Group = "worker" | "parent" | "elderly";
export type Language = "en" | "hi";
export type Channel = "whatsapp" | "sms";
export type Home = "pucca" | "tin";

export interface Subscription {
  phone: string;
  wardId: string;
  group: Group;
  language: Language;
  channel: Channel;
  home?: Home;
  caregiverPhone?: string;
}

const BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(body.message ?? `Request failed (${res.status})`, res.status);
  return body as T;
}

// Without VITE_API_URL, or when the live API can't be reached, the map reads the static
// snapshot written by data/scripts/build_snapshot.py into public/snapshot/.
let useSnapshot = !BASE;

async function snapshot<T>(path: string): Promise<T> {
  const res = await fetch(`${import.meta.env.BASE_URL}snapshot/${path}`);
  if (!res.ok) throw new ApiError(`Snapshot missing (${res.status})`, res.status);
  return (await res.json()) as T;
}

export const isLive = () => !useSnapshot;

export const api = {
  wards: async (): Promise<WardCollection> => {
    if (!useSnapshot) {
      try {
        return await request<WardCollection>("/wards");
      } catch {
        useSnapshot = true;
      }
    }
    return snapshot<WardCollection>("wards.json");
  },
  forecast: (wardId: string) =>
    useSnapshot
      ? snapshot<WardForecast>(`forecast/${encodeURIComponent(wardId)}.json`)
      : request<WardForecast>(`/wards/${encodeURIComponent(wardId)}/forecast`),
  resources: () => (useSnapshot ? snapshot<PlaceCollection>("resources.json") : request<PlaceCollection>("/resources")),
  subscribe: (sub: Subscription) => request<{ ok: true }>("/subscribe", { method: "POST", body: JSON.stringify(sub) }),
};
