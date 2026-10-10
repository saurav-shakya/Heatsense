import type { Language, WardProps } from "../api/client";
import type { Strings } from "../i18n/strings";
import { downloadCsv, rankWards, wardsCsv } from "../lib/export";
import LevelChip from "./LevelChip";

interface Props {
  wards: WardProps[];
  day: number;
  lang: Language;
  t: Strings;
  onSelect: (wardId: string) => void;
}

/** Ranked top 10 for ward officers: a true ranking, so it is numbered. The full list exports as CSV. */
export default function TopWards({ wards, day, lang, t, onSelect }: Props) {
  const ranked = rankWards(wards, day).slice(0, 10);
  const exportList = () => {
    const date = wards.find((w) => w.daily?.[day])?.daily?.[day].date ?? "forecast";
    downloadCsv(`heatshield-wards-${date}.csv`, wardsCsv(wards, day, lang, t));
  };

  return (
    <section className="top-wards" aria-labelledby="top-title">
      <h2 id="top-title" className="section-title">
        {t.topWards}
      </h2>
      <p className="section-note">{t.topWardsNote}</p>
      <ol>
        {ranked.map((w, i) => {
          const d = w.daily![day];
          return (
            <li key={w.wardId}>
              <button className="ward-row" onClick={() => onSelect(w.wardId)}>
                <span className="rank">{i + 1}</span>
                <span className="ward-name">{w.name}</span>
                <LevelChip level={d.level} t={t} />
                <span className="score">{d.risk.toFixed(2)}</span>
              </button>
            </li>
          );
        })}
      </ol>
      {ranked.length > 0 && (
        <button className="button-quiet export" onClick={exportList}>
          {t.exportCsv}
        </button>
      )}
    </section>
  );
}
