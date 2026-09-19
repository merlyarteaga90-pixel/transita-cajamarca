import type { ApiRoute } from '../api/types';
import { formatFare, formatSchedule, hasValue } from '../lib/formatters';

export type RouteMetaBadgesProps = {
  route: ApiRoute;
};

export function RouteMetaBadges({ route }: RouteMetaBadgesProps) {
  const schedule = formatSchedule(route);
  const generalFare = formatFare(route.tarifa_general ?? route.tarifa);
  const halfFare = formatFare(route.tarifa_medio_pasaje);

  const badges: Array<{ key: string; icon: string; label: string; value: string }> = [];

  if (hasValue(schedule)) {
    badges.push({ key: 'horario', icon: '🕐', label: 'Horario', value: schedule });
  }
  if (hasValue(generalFare)) {
    badges.push({ key: 'tarifa-general', icon: '🪙', label: 'General', value: generalFare });
  }
  if (hasValue(halfFare)) {
    badges.push({ key: 'tarifa-medio', icon: '🎓', label: 'Medio', value: halfFare });
  }

  if (!badges.length) return null;

  return (
    <div className="ruta-meta-row">
      {badges.map((badge) => (
        <span key={badge.key} className="ruta-meta-badge" data-meta={badge.key}>
          <span className="ruta-meta-icon">{badge.icon}</span>
          <span className="ruta-meta-label">{badge.label}</span>
          <span className="ruta-meta-value">{badge.value}</span>
        </span>
      ))}
    </div>
  );
}
