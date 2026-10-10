import type { RiskLevel } from "../api/client";
import type { Strings } from "../i18n/strings";

export default function LevelChip({ level, t }: { level: RiskLevel; t: Strings }) {
  return <span className={`chip risk-${level}`}>{t.levels[level]}</span>;
}
