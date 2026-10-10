import type { Language } from "../api/client";

const IST = "Asia/Kolkata";
const locale = (lang: Language) => (lang === "hi" ? "hi-IN" : "en-IN");

/** "2026-10-11" -> "Sun 11 Oct" (rendered as an IST calendar date). */
export function dayLabel(date: string, lang: Language): string {
  return new Date(`${date}T12:00:00+05:30`).toLocaleDateString(locale(lang), {
    weekday: "short",
    day: "numeric",
    month: "short",
    timeZone: IST,
  });
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
