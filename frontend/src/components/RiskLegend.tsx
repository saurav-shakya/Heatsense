import { LEVELS } from "../api/client";
import type { Strings } from "../i18n/strings";

export default function RiskLegend({ t }: { t: Strings }) {
  return (
    <section className="legend" aria-labelledby="legend-title">
      <h2 id="legend-title" className="section-title">
        {t.legend}
      </h2>
      <dl>
        {LEVELS.map((lvl) => (
          <div key={lvl} className="legend-row">
            <dt>
              <span className={`swatch risk-${lvl}`} aria-hidden="true" />
              {t.levels[lvl]}
            </dt>
            <dd>{t.levelAdvice[lvl]}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
