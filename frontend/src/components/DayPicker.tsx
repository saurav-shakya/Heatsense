import { LEVELS, type WardProps } from "../api/client";
import type { Strings } from "../i18n/strings";

interface Props {
  wards: WardProps[];
  day: number;
  onChange: (day: number) => void;
  dayName: (i: number) => string;
  t: Strings;
}

/** Four forecast days as radio options; each shows how wards split across risk levels that day. */
export default function DayPicker({ wards, day, onChange, dayName, t }: Props) {
  const days = wards[0]?.daily?.length ?? 0;

  return (
    <fieldset className="day-picker">
      <legend className="label">{t.chooseDay}</legend>
      <div className="day-options">
        {Array.from({ length: days }, (_, i) => {
          const counts = LEVELS.map((lvl) => wards.filter((w) => w.daily?.[i]?.level === lvl).length);
          const summary = LEVELS.map((lvl, j) => `${t.levels[lvl]} ${counts[j]}`).join(", ");
          return (
            <label key={i} className="day-option" data-selected={i === day || undefined}>
              <input
                type="radio"
                name="forecast-day"
                value={i}
                checked={i === day}
                onChange={() => onChange(i)}
                className="visually-hidden"
              />
              <span className="day-name">{dayName(i)}</span>
              <span className="dist-bar" title={summary} aria-label={summary}>
                {LEVELS.map((lvl, j) =>
                  counts[j] > 0 ? (
                    <span key={lvl} className={`dist-seg risk-${lvl}`} style={{ flexGrow: counts[j] }} />
                  ) : null,
                )}
              </span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
