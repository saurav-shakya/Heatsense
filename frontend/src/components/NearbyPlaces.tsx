import type { Language } from "../api/client";
import type { Strings } from "../i18n/strings";
import { clockLabel } from "../lib/format";
import type { NearPlace } from "../lib/geo";

interface Props {
  places: NearPlace[];
  lang: Language;
  t: Strings;
}

export default function NearbyPlaces({ places, lang, t }: Props) {
  if (places.length === 0) return <p className="section-note">{t.noPlaces}</p>;
  const km = (n: number) => `${n.toFixed(1)} ${lang === "hi" ? "किमी" : "km"}`;
  return (
    <>
      <ul className="places">
        {places.map((p) => (
          <li key={p.id}>
            <span className={`place-dot place-${p.kind}`} aria-hidden="true" />
            <span className="place-name">
              {lang === "hi" && p.nameHi ? p.nameHi : p.name}
              {!p.verified && <span className="tag">{t.placeSample}</span>}
            </span>
            <span className="place-meta">
              {t.placeKinds[p.kind]} · {km(p.km)} ·{" "}
              {p.hours ? t.placeHours(clockLabel(p.hours[0], lang), clockLabel(p.hours[1], lang)) : t.alwaysOpen}
            </span>
          </li>
        ))}
      </ul>
      {places.some((p) => !p.verified) && <p className="section-note">{t.placesSampleNote}</p>}
    </>
  );
}
