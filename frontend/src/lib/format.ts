import type { Language } from "../api/client";

const IST = "Asia/Kolkata";
const locale = (lang: Language) => (lang === "hi" ? "hi-IN" : "en-IN");

/** "2026-10-11" -> "Sun 11 Oct" (rendered as an IST calendar date); withYear -> "11 Oct 2026". */
export function dayLabel(date: string, lang: Language, withYear = false): string {
  return new Date(`${date}T12:00:00+05:30`).toLocaleDateString(
    locale(lang),
    withYear
      ? { day: "numeric", month: "long", year: "numeric", timeZone: IST }
      : { weekday: "short", day: "numeric", month: "short", timeZone: IST },
  );
}

/** UTC ISO -> "2 pm" in Delhi time. */
export function hourLabel(iso: string, lang: Language): string {
  return new Date(iso).toLocaleTimeString(locale(lang), { hour: "numeric", timeZone: IST });
}

/** UTC ISO -> IST calendar date "YYYY-MM-DD". */
export function istDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-CA", { timeZone: IST });
}

export function todayLong(lang: Language): string {
  return new Date().toLocaleDateString(locale(lang), {
    weekday: "long",
    day: "numeric",
    month: "long",
    timeZone: IST,
  });
}

const hiPart = (h: number) => (h >= 4 && h < 12 ? "सुबह" : h >= 12 && h < 16 ? "दोपहर" : h >= 16 && h < 19 ? "शाम" : "रात");

/** IST hour (0-24) -> "2 pm" / "दोपहर 2 बजे", for work plans and opening hours (same words as the alerts). */
export function clockLabel(hour: number, lang: Language): string {
  if (lang === "hi") return `${hiPart(hour % 24)} ${hour % 12 || 12} बजे`;
  const d = new Date(Date.UTC(2026, 0, 1, hour % 24, 0) - 5.5 * 3_600_000);
  return d.toLocaleTimeString(locale(lang), { hour: "numeric", timeZone: IST });
}

/** IST hours [from, to) -> "11 am to 5 pm". */
export function hourRange(from: number, to: number, lang: Language): string {
  // The end hour is exclusive, so name its part of day from the hour before: 12-4 pm is all दोपहर.
  return lang === "hi"
    ? `${hiPart(from % 24)} ${from % 12 || 12} से ${hiPart((to - 1) % 24)} ${to % 12 || 12} बजे तक`
    : `${clockLabel(from, lang)} to ${clockLabel(to, lang)}`;
}
