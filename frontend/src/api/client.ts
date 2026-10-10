// Typed client for the HeatShield HTTP API (backend/functions/api/app.py).

import type { Polygon } from "geojson";

export type RiskLevel = "low" | "moderate" | "high" | "extreme";
export const LEVELS: RiskLevel[] = ["low", "moderate", "high", "extreme"];

export interface DailyRisk {
  date: string; // IST calendar date, YYYY-MM-DD
  risk: number; // 0..1
  level: RiskLevel;
  heatIndex: number; // deg C at the peak hour
  peakAt: string; // UTC ISO of the peak hour
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
}

export interface WardForecast {
  ward: WardProps;
  hourly: HourlyRisk[];
}

export type Group = "worker" | "parent" | "elderly";
export type Language = "en" | "hi";
export type Channel = "whatsapp" | "sms";

export interface Subscription {
  phone: string;
  wardId: string;
  group: Group;
  language: Language;
  channel: Channel;
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

export const api = {
  wards: () => request<WardCollection>("/wards"),
  forecast: (wardId: string) => request<WardForecast>(`/wards/${encodeURIComponent(wardId)}/forecast`),
  subscribe: (sub: Subscription) => request<{ ok: true }>("/subscribe", { method: "POST", body: JSON.stringify(sub) }),
};
