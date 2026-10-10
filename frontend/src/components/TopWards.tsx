import type { WardProps } from "../api/client";
import type { Strings } from "../i18n/strings";
import LevelChip from "./LevelChip";

interface Props {
  wards: WardProps[];
  day: number;
  t: Strings;
  onSelect: (wardId: string) => void;
}

/** Ranked top 10 for ward officers: a true ranking, so it is numbered. */
export default function TopWards({ wards, day, t, onSelect }: Props) {
  const ranked = wards
    .filter((w) => w.daily?.[day])
    .sort((a, b) => b.daily![day].risk - a.daily![day].risk)
    .slice(0, 10);

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
    </section>
  );
}
