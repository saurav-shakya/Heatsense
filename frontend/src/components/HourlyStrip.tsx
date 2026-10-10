import type { HourlyRisk, Language } from "../api/client";
import type { Strings } from "../i18n/strings";
import { hourLabel } from "../lib/format";

interface Props {
  hours: HourlyRisk[];
  lang: Language;
  t: Strings;
}

/** 24 cells, one per hour of the chosen day, coloured by risk level. Each cell has its own tooltip. */
export default function HourlyStrip({ hours, lang, t }: Props) {
  if (hours.length === 0) return <div className="hourly-strip is-empty" aria-hidden="true" />;

  return (
    <figure className="hourly">
      <ol className="hourly-strip">
        {hours.map((h) => {
          const label = `${hourLabel(h.forecastTime, lang)}: ${t.levels[h.level]}, ${Math.round(h.heatIndex)}°C`;
          return (
            <li key={h.forecastTime} className={`hour risk-${h.level}`} title={label}>
              <span className="visually-hidden">{label}</span>
            </li>
          );
        })}
      </ol>
      <div className="hourly-axis" aria-hidden="true">
        {[0, 6, 12, 18].map((i) => (
          <span key={i} style={{ gridColumn: `${i + 1} / span 6` }}>
            {hours[i] ? hourLabel(hours[i].forecastTime, lang) : ""}
          </span>
        ))}
      </div>
    </figure>
  );
}
