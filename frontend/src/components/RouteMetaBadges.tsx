import { Clock, Coins, GraduationCap } from 'lucide-react';
import type { ReactNode } from 'react';
import type { ApiRoute } from '../api/types';
import { formatFare, formatSchedule, hasValue } from '../lib/formatters';

export type RouteMetaBadgesProps = {
  route: ApiRoute;
  asHeaderContent?: boolean;
};

export function RouteMetaBadges({ route, asHeaderContent = false }: RouteMetaBadgesProps) {
  const schedule = formatSchedule(route);
  const generalFare = formatFare(route.tarifa_general ?? route.tarifa);
  const halfFare = formatFare(route.tarifa_medio_pasaje);

  type BadgeEntry = { key: string; icon: ReactNode; label: string; value: string };
  const badges: BadgeEntry[] = [];

  if (hasValue(schedule)) {
    badges.push({ key: 'horario', icon: <Clock size={12} strokeWidth={2.5} aria-hidden="true" />, label: 'Horario', value: schedule });
  }
  if (hasValue(generalFare)) {
    badges.push({ key: 'tarifa-general', icon: <Coins size={12} strokeWidth={2.5} aria-hidden="true" />, label: 'General', value: generalFare });
  }
  if (hasValue(halfFare)) {
    badges.push({ key: 'tarifa-medio', icon: <GraduationCap size={12} strokeWidth={2.5} aria-hidden="true" />, label: 'Medio', value: halfFare });
  }

  if (!badges.length) return null;

  const className = asHeaderContent ? 'ruta-header-meta' : 'ruta-meta-row';

  return (
    <div className={className}>
      {badges.map((badge) => (
        <span key={badge.key} className="ruta-meta-badge" data-meta={badge.key}>
          <span className="ruta-meta-icon">{badge.icon}</span>
          {!asHeaderContent && <span className="ruta-meta-label">{badge.label}</span>}
          <span className="ruta-meta-value">{badge.value}</span>
        </span>
      ))}
    </div>
  );
}
