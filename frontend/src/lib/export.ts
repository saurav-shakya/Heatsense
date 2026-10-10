import type { Language, WardProps } from "../api/client";
import type { Strings } from "../i18n/strings";
import { hourLabel } from "./format";

/** Every ward with a forecast for `day`, highest risk first. */
export function rankWards(wards: WardProps[], day: number): WardProps[] {
  return wards.filter((w) => w.daily?.[day]).sort((a, b) => b.daily![day].risk - a.daily![day].risk);
}

function cell(value: string | number): string {
  const s = String(value);
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/** Ranked ward list for ward officers, as CSV text. */
export function wardsCsv(wards: WardProps[], day: number, lang: Language, t: Strings): string {
  const rows = rankWards(wards, day).map((w, i) => {
    const d = w.daily![day];
    return [i + 1, w.wardId, w.name, d.date, t.levels[d.level], d.risk.toFixed(3), Math.round(d.heatIndex), hourLabel(d.peakAt, lang)];
  });
  return [t.csvHeaders, ...rows].map((r) => r.map(cell).join(",")).join("\r\n");
}

/** Save the CSV with a BOM so Excel opens Hindi text correctly. */
export function downloadCsv(filename: string, csv: string): void {
  const url = URL.createObjectURL(new Blob(["﻿", csv], { type: "text/csv;charset=utf-8" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
