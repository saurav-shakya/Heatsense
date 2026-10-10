import type { DailyRisk, Language } from "../api/client";
import type { Strings } from "../i18n/strings";
import { hourRange } from "../lib/format";

interface Props {
  day: DailyRisk;
  lang: Language;
  t: Strings;
}

/** Stop-work hours and work-rest ratios for moderate outdoor work, from the day's WBGT estimate. */
export default function WorkPlan({ day, lang, t }: Props) {
  const plan = day.workPlan ?? [];
  return (
    <>
      {plan.length === 0 ? (
        <p>{t.workSafe}</p>
      ) : (
        <ul className="plain-list">
          {plan.map((seg) => (
            <li key={seg.from} className={seg.work === 0 ? "is-stop" : undefined}>
              {seg.work === 0
                ? t.workStop(hourRange(seg.from, seg.to, lang))
                : t.workRatio(hourRange(seg.from, seg.to, lang), seg.work)}
            </li>
          ))}
        </ul>
      )}
      {day.wbgtMax !== undefined && <p className="section-note">{t.wbgtNote(day.wbgtMax)}</p>}
    </>
  );
}
