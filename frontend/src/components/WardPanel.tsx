import { useEffect, useState } from "react";
import { api, type HourlyRisk, type Language, type WardProps } from "../api/client";
import type { Strings } from "../i18n/strings";
import { hourLabel, istDate } from "../lib/format";
import HourlyStrip from "./HourlyStrip";
import LevelChip from "./LevelChip";
import SubscribeForm from "./SubscribeForm";

interface Props {
  ward: WardProps;
  day: number;
  lang: Language;
  t: Strings;
  onBack: () => void;
}

export default function WardPanel({ ward, day, lang, t, onBack }: Props) {
  const [hourly, setHourly] = useState<HourlyRisk[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api
      .forecast(ward.wardId)
      .then((r) => setHourly(r.hourly))
      .catch(() => setFailed(true));
  }, [ward.wardId]);

  const today = ward.daily?.[day];
  const hours = hourly?.filter((h) => today && istDate(h.forecastTime) === today.date) ?? [];

  return (
    <article className="ward-panel" aria-labelledby="ward-title">
      <button className="button-quiet back" onClick={onBack}>
        {t.backToList}
      </button>
      <header className="ward-head">
        <h2 id="ward-title" className="ward-title">
          {ward.name}
        </h2>
        {today && <LevelChip level={today.level} t={t} />}
      </header>
      {today ? (
        <p className="ward-peak">{t.peakAt(today.heatIndex, hourLabel(today.peakAt, lang))}</p>
      ) : (
        <p className="ward-peak">{t.noForecast}</p>
      )}

      <section aria-labelledby="hourly-title">
        <h3 id="hourly-title" className="label">
          {t.hourByHour}
        </h3>
        {failed ? <p className="section-note">{t.loadFailed}</p> : <HourlyStrip hours={hours} lang={lang} t={t} />}
      </section>

      <section aria-labelledby="why-title">
        <h3 id="why-title" className="label">
          {t.whyTitle}
        </h3>
        <dl className="factors">
          <div>
            <dt>{t.surfaceHeat}</dt>
            <dd>{t.surfaceHeatValue(ward.lstOffset)}</dd>
          </div>
          <div>
            <dt>{t.greenCover}</dt>
            <dd>{t.greenCoverValue(ward.ndvi)}</dd>
          </div>
          <div>
            <dt>{t.density}</dt>
            <dd>{t.densityValue(ward.popDensity)}</dd>
          </div>
        </dl>
      </section>

      <SubscribeForm wardId={ward.wardId} lang={lang} t={t} />
    </article>
  );
}
