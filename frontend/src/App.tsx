import { useCallback, useEffect, useMemo, useState } from "react";
import { api, type Language, type WardCollection } from "./api/client";
import DayPicker from "./components/DayPicker";
import RiskLegend from "./components/RiskLegend";
import TopWards from "./components/TopWards";
import WardMap from "./components/WardMap";
import WardPanel from "./components/WardPanel";
import { STRINGS } from "./i18n/strings";
import { dayLabel, todayLong } from "./lib/format";

type Load = { state: "loading" } | { state: "error" } | { state: "ready"; data: WardCollection };

function initialLanguage(): Language {
  try {
    const saved = localStorage.getItem("heatshield.lang");
    if (saved === "en" || saved === "hi") return saved;
  } catch {
    /* storage unavailable: fall through */
  }
  return navigator.language.startsWith("hi") ? "hi" : "en";
}

export default function App() {
  const [lang, setLang] = useState<Language>(initialLanguage);
  const [load, setLoad] = useState<Load>({ state: "loading" });
  const [day, setDay] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const t = STRINGS[lang];

  const fetchWards = useCallback(() => {
    setLoad({ state: "loading" });
    api
      .wards()
      .then((data) => setLoad({ state: "ready", data }))
      .catch(() => setLoad({ state: "error" }));
  }, []);

  useEffect(fetchWards, [fetchWards]);

  useEffect(() => {
    document.documentElement.lang = lang;
    try {
      localStorage.setItem("heatshield.lang", lang);
    } catch {
      /* ignore */
    }
  }, [lang]);

  const wards = load.state === "ready" ? load.data.features.map((f) => f.properties) : [];
  const dates = wards[0]?.daily?.map((d) => d.date) ?? [];
  const dayName = (i: number) =>
    i === 0 ? t.dayToday : i === 1 ? t.dayTomorrow : dates[i] ? dayLabel(dates[i], lang) : "";

  const atRisk = useMemo(
    () => wards.filter((w) => ["high", "extreme"].includes(w.daily?.[day]?.level ?? "")).length,
    [wards, day],
  );
  const selectedWard = wards.find((w) => w.wardId === selected) ?? null;

  return (
    <div className="page">
      <header className="masthead">
        <p className="wordmark">
          HeatShield <span className="wordmark-city">{t.city}</span>
        </p>
        <p className="masthead-date">{todayLong(lang)}</p>
        <div className="lang-switch" role="group" aria-label="Language / भाषा">
          <button aria-pressed={lang === "en"} onClick={() => setLang("en")}>
            English
          </button>
          <button aria-pressed={lang === "hi"} onClick={() => setLang("hi")} lang="hi">
            हिन्दी
          </button>
        </div>
      </header>

      <main className="layout">
        <aside className="side">
          <section className="lead" aria-live="polite">
            {load.state === "loading" && <p className="status">{t.loading}</p>}
            {load.state === "error" && (
              <div className="status status-error">
                <p>{t.loadFailed}</p>
                <button className="button-quiet" onClick={fetchWards}>
                  {t.retry}
                </button>
              </div>
            )}
            {load.state === "ready" && (
              <>
                <h1 className="headline">
                  {atRisk > 0 ? t.headline(dayName(day), atRisk, wards.length) : t.headlineCalm(dayName(day))}
                </h1>
                <p className="standfirst">{t.standfirst}</p>
                <DayPicker wards={wards} day={day} onChange={setDay} dayName={dayName} t={t} />
              </>
            )}
          </section>

          {load.state === "ready" && (
            <section className="detail">
              {selectedWard ? (
                <WardPanel
                  key={selectedWard.wardId}
                  ward={selectedWard}
                  day={day}
                  lang={lang}
                  t={t}
                  onBack={() => setSelected(null)}
                />
              ) : (
                <TopWards wards={wards} day={day} t={t} onSelect={setSelected} />
              )}
              <RiskLegend t={t} />
              <p className="sample-note">{t.sampleData}</p>
            </section>
          )}
        </aside>

        <div className="map-area">
          {load.state === "ready" && (
            <WardMap data={load.data} day={day} selected={selected} onSelect={setSelected} t={t} />
          )}
        </div>
      </main>
    </div>
  );
}
